from nltk.sentiment.vader import SentimentIntensityAnalyzer
from nltk import tokenize
import pandas as pd
import spacy

if __name__ == "__main__":
    sid = SentimentIntensityAnalyzer()
    sid.polarity_scores('hello world. what a nice day!')

    with open('../../backtester/data/news/news_coindesk.csv', 'r') as f:
        df = pd.read_csv(f)

    df = df[df['Headline']!='Headline']

    nlp = spacy.load('en')

    doc = nlp(u'London is a big city in the United Kingdom.')
    print(doc[0].text, doc[0].ent_iob, doc[0].ent_type_)


    # do some simple document clustering using tf-idf and PCA
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.feature_extraction.stop_words import ENGLISH_STOP_WORDS

    vectorizer = TfidfVectorizer(stop_words=ENGLISH_STOP_WORDS)

    vectors = vectorizer.fit_transform(df['Content'].values.tolist())
    
    from sklearn.decomposition import TruncatedSVD    
    svd = TruncatedSVD(n_components=100)

    vectors100d = svd.fit_transform(vectors)

    from tsne import bh_sne
    vectors2d = bh_sne(vectors100d)
    df['Embedding'] = vectors2d.tolist()

    from sklearn.cluster import KMeans
    kmeans = KMeans(n_clusters=5)
    clusters = kmeans.fit_predict(vectors100d)
    df['Cluster'] = clusters

    from bokeh.plotting import show, ColumnDataSource, figure
    from bokeh.charts import Scatter
    from bokeh.models import LabelSet
    from pandas.core.frame import DataFrame
    from bokeh.models import HoverTool
    from bokeh.palettes import Spectral6

    source = ColumnDataSource(data=dict(x_coord=vectors2d[:,0].tolist(),
                            y_coord=vectors2d[:,1].tolist(),
                            headlines=df['Headline'].values.tolist()))
    p = figure(plot_width=600, plot_height=600, tools=['box_zoom'])    
    colours = [Spectral6[cl] for cl in clusters]
    p.circle('x_coord', 'y_coord', size=5, source=source, color=colours)
    hover = HoverTool(tooltips=[("Headline:", "@headlines")])
    p.add_tools(hover)
    show(p)

    import matplotlib.pyplot as plt
    # now compare this to the bitcoin price
    with open('../../backtester/data/bitcoin_4_years.csv', 'r') as f:
        prices = pd.read_csv(f)
        prices = prices[['Timestamp', 'Weighted Price']]
        prices['Weighted Price'] = prices['Weighted Price'].apply(lambda x: float(x))
        prices.set_index('Timestamp', inplace=True)
    prices.plot()
    plt.show()