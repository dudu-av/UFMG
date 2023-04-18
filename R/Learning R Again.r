# import 'ggplot2' library
library(ggplot2);

# view 'msleep' as a table
View(msleep);

### Numeric Data

# shows the 6 first datas
head(msleep);
# shows the 6 last datas
tail(msleep);
# shows the dimensions of the dataframe
dim(msleep);
# shows the type of each column and some values
str(msleep);
# shows the name of each column
names(msleep);

# to include 'msleep' in the envionment
data(msleep);

# shows some statistics
summary(msleep)
# to access a column, use the $ after the dataframe name
mean(msleep$sleep_total)
# standard deviation
sd(msleep$sleep_total)
# quantiles
quantile(msleep$sleep_total)

# to check how many animals sleep more than 8h a day
sum(msleep$sleep_total > 8)
# to exclude the NAs from the calculation, use na.rm = TRUE
mean(msleep$sleep_rem, na.rm = TRUE)
# to calculate the correlation only with complete data, put use = "complete.obs"
cor(msleep$sleep_total, msleep$sleep_rem, use = "complete.obs")


### Categorical Data

# shows the amount of each value
table(msleep$vore)
# shows the proportion of the amount of each value
prop.table(table(msleep$vore))
# shows the proportion between two variables, per row
# (sum of the values in a row result in 1)
prop.table(table(msleep$vore, msleep$conservation), margin = 1)
# per column
prop.table(table(msleep$vore, msleep$conservation), margin = 2)

### Plotting Data
## Tips: para fazer os rótulos do eixo x inclinarem, faça:
## + theme(axis.text.x = element_text(angle = 45, hjust=1))
# R plot
plot(msleep$sleep_total, msleep$sleep_rem)
# ggplot2 plot (o "x =" e o "y = " podem ser tirados)
ggplot(msleep, aes(x = sleep_total, y = sleep_rem)) + geom_point()
# putting labels and colors
ggplot(msleep, aes(sleep_total, sleep_rem)) +
  geom_point(colour = "red") +
  xlab("Total sleep time (h)") +
  ylab("Total rem sleep time (h)")
# coloring the points by the vore class, putting limits and scaling
ggplot(msleep, aes(sleep_total, sleep_rem, colour = vore)) +
  geom_point() +
  xlab("Total sleep time (h)") +
  ylab("Total rem sleep time (h)") +
  xlim(0, 15) + 
  scale_x_log10()
# separating by vore class
ggplot(msleep, aes(sleep_total, sleep_rem)) +
  geom_point() +
  xlab("Total sleep time (h)") +
  ylab("Total rem sleep time (h)") +
  scale_x_log10() + 
  facet_wrap(~ vore)

### Other Graphs
# R boxplot
boxplot(sleep_total ~ vore, data = msleep)
# ggplot boxplot
ggplot(msleep, aes(vore, sleep_total)) + geom_boxplot()
# ggplot histogram
ggplot(msleep, aes(sleep_total)) + geom_histogram()
# ggplot bar chart for categorical data
ggplot(msleep, aes(vore)) + geom_bar()
# ggplot for one bar with porcentages
ggplot(msleep, aes(factor(1), fill = vore)) + geom_bar()

# saving plots
# (with a var like myplot, ggsave saves the last plot done)
myplot <- ggplot(msleep, aes(factor(1), fill = vore)) + geom_bar()
ggsave("a_plot.pdf", myplot, width = 5, height = 5)

### Data Types
# shows the kind of data
class(3.5)
class(2L)
class("a")
class(msleep)
# Matrixes store just one kind of data (e.g.: everything char)
# data.frame, data.table and tibbles (tbl_df) store different kinds of data,
# but data.frame is the slowes and data.table the fastest
# data.tables must be imported with library(data.table)
library(data.table)
# usually, to convert from one to the other you just need to do
# as.<data type you want>(...)
ms <- as.data.table(msleep)

### Matrix
?matrix
matrix(1:6, nrow = 2)
matrix(1:6, nrow = 2, byrow = TRUE)

### String
phrase <- "como maçãs, bananas, melancias"
# Size of a string
nchar(phrase)
# Concatenate
paste(phrase, "etc", sep = ", ")
# Split a string
strsplit(phrase, " ")
# Take a substring
substr(phrase, 1, 4)

### Functions to use with data tables
# SEE: https://cran.r-project.org/web/packages/data.table/vignettes/datatable-intro.html
# LOOK FOR HOW TO USE DPLYR, TIDYVERSE AND PURRR
# Delete a row with index i
dt <- dt[-i]
# Delete rows with index i, j and k
dt <- dt[-c(i,j,k)]
# Delete a column with name index
dt$index <- NULL
# Apply a function to a column i, grouping by other j
dt[, sum(i), by = j]