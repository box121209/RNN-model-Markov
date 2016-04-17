#!/usr/bin/Rscript

args <- commandArgs(trailingOnly=T)

filename <- args[1]
infile <- sprintf("%s.txt", filename)
outfile <- sprintf("%s.pdf", filename)

library(igraph)

family <- readLines(infile)
n <- length(family)
g <- make_empty_graph(n=n, directed=FALSE)
V(g)$name <- family

for(i in 1:(n-1)){
  for(j in (i+1):n){
    s1 <- strsplit(family[i],"")[[1]]
    s2 <- strsplit(family[j],"")[[1]]
    wt <- length(intersect(s1, s2))
    if(wt>0) g <- add.edges(g, c(i,j), attr=list(weight=wt))
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



