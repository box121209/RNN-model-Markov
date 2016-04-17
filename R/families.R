#!/usr/bin/Rscript

args <- commandArgs(trailingOnly=T)

path <- args[1]

charfile <- sprintf("%s/chars.txt", path)
famfile <- sprintf("%s/families.txt", path)
distfile <- sprintf("%s/distributions.txt", path)
outfile <- sprintf("%s/families.pdf", path)

# parse the data:
chars <- sort(readLines(charfile))
family <- lapply(readLines(famfile), function(s){ sort(strsplit(s,"")[[1]]) })
distr0 <- lapply(readLines(distfile), function(s){ as.numeric(strsplit(s, " ")[[1]]) })
n <- length(distr0)
distr <- lapply(1:n, function(i){
  f <- family[i][[1]]
  d <- distr0[[i]]
  df0 <- data.frame(chars, rep(0.0, length(chars)))
  df1 <- data.frame(f,d)
  df <- merge(df0, df1, by.x='chars', by.y='f', all=TRUE)
  sapply(df[,3], function(x) if(is.na(x)) 0 else x)
})

# compute distance matrix:
KLdiv <- function(d1, d2){
  sqrt(sum((d1-d2)^2))
}
n <- length(family)
dmat <- matrix(nrow=n, ncol=n)
for(i in 1:n)
  for(j in 1:n)
    dmat[i,j] <- KLdiv(distr[[i]], distr[[j]])

# build graph:
library(igraph)

n <- length(family)
g <- make_empty_graph(n=n, directed=FALSE)
V(g)$name <- readLines(famfile)

for(i in 1:(n-1)){
  for(j in (i+1):n){
    s1 <- family[[i]]
    s2 <- family[[j]]
    wt <- length(intersect(s1, s2))
    if(wt>0) g <- add.edges(g, c(i,j), attr=list(weight=1/dmat[i,j]))
  }
}

E(g)$width <- E(g)$weight^2
V(g)$size <- 8 * sapply(V(g)$name, nchar)
V(g)$color <- 'white'
V(g)$frame.color <- 'blue'
V(g)$label <- sapply(1:vcount(g), function(i) sprintf("%d\n%s", i-1, V(g)$name[i]))

pdf(outfile)
plot(g)
dev.off()



