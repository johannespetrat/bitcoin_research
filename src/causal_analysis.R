args = commandArgs(trailingOnly=TRUE)
print(args)
if (length(args)!=3) {
  stop("Provide split date, pre_period_length (days) and post_period_length (days)")
}
split_date <- args[1]
pre_period_length <- as.integer(args[2])
post_period_length <- as.integer(args[3])
# Causal Impact
library(CausalImpact)

set.seed(1)

df = read.table('/Users/Johannes/Documents/projects/quanttrading/bitcoin/backtester/data/combined_train_2015.csv',
                sep = ",", header=TRUE)

df$Timestamp <- as.Date(df$Timestamp , "%Y-%m-%d %H:%M:%S")
drops <- c("Timestamp","Datetime")
data <- zoo(cbind(df[ , !(names(df) %in% drops)]), df$Timestamp)
#pre.period <- as.Date(c("2013-01-01", "2013-11-25"))
#post.period <- as.Date(c("2013-11-26", "2014-08-31"))
#pre.period <- as.Date(c("2013-01-01", "2013-08-15"))
#post.period <- as.Date(c("2013-08-16", "2013-10-31"))
pre.period <- c(as.Date(split_date) - pre_period_length, as.Date(split_date)-1)
post.period <- c(as.Date(split_date), as.Date(split_date) + post_period_length)
impact <- CausalImpact(data, pre.period, post.period)
#plot(impact)
#summary(impact, 'report')
write.table(impact$summary, file = "causal_tmp.csv")