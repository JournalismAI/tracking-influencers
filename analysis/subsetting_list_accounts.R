library(tidyverse)
library(jsonlite)
library(reshape2)
library(tibble)

accounts_scraped=stream_in(file("profiles.json")) #File provided by the tech team after scraping profile information of list of accounts

# Reducing the list of accounts

## 1 - Getting only those accounts which contains a mum/dad related word either in the username or in the bio.

subset_mum=accounts_scraped %>% mutate(biography=tolower(biography), username=tolower(username)) %>%  
  filter(grepl(pattern = "mum|mummy|mother|motherhood|mom|parent|parenting|parenthood|father|dad|daddy|mama|dadda|mami|madre|maternidad|paternidad|papa|padre|papi|mamma|maternita|paternita|genitor|famiglia", username) |
           grepl(pattern = "mum|mummy|mother|motherhood|mom|parent|parenting|parenthood|father|dad|daddy|mama|dadda|mami|madre|maternidad|paternidad|papa|padre|papi|mamma|maternita|paternita|genitor|famiglia", biography))

subset_mum %>% group_by(groupId) %>% count()
## That gives a total of 303 accounts for Infobae, 164 for Il Sole and 855 for Sky News


## 2 - Reducing number of accounts by removing those with fewer posts. 
## Different approach depending on the organisation here as the number of accounts differs widely as well as the characteristics of each population

subset_mum%>% filter(postsCount<10000) %>% #removing extreme outlier form Sky News
  ggplot(aes(x=postsCount)) +
  geom_histogram()+facet_wrap(~groupId, scales = "free")

subset_mum  %>% filter(postsCount<10000) %>% #removing extreme outlier form Sky News
  ggplot(aes(y=postsCount, x=groupId))+geom_boxplot()+coord_flip()+
  geom_hline(yintercept=100, linetype="dashed", color = "red", size=1)+
  geom_hline(yintercept=1000, linetype="dashed", color = "blue", size=1)

## Histograms and boxplot shows differences in the distribution of the posts. 
## Il Sole's accounts have higher number of posts per account. Sky News has more outliers over the fourth quartile. The population of Infobae is similar to Sky News but fewer number of accounts. 
## Reducing the number of accounts by removing the top 1% by number of posts and the bottom 25%, for Sky News and Infobae. 
## As Il Sole has a significant lower number of accounts compared with the other two organisations, it has reduced the bottom 5%. 

subset_mum %>% group_by(groupId) %>% summarise(meanPost=mean(postsCount), 
                                               maxPost=max(postsCount),
                                               minPost=min(postsCount),
                                               firstQuan=quantile(postsCount,0.25),
                                               bottom10=quantile(postsCount,0.10),
                                               bottom5=quantile(postsCount,0.05),
                                               top1=quantile(postsCount,0.99))

subset_mum %>% filter(groupId=="kids-sole" & postsCount>=144 &postsCount<=4595) %>% rbind(
  subset_mum %>% filter(groupId=="kids-infobae" & postsCount>=189 &postsCount<=3099)
) %>% rbind(subset_mum %>% filter(groupId=="kids-sky-news" & postsCount>200 &postsCount<4031)) %>% 
  group_by(groupId) %>% summarise(accounts=n())

## This results in 223 for Infobae, and 153 accounts for Il Sole but 631 for Sky News. 

## 3 - Reducing by the number of followers

subset_mum%>% filter(subscribersCount<400000) %>% #removing extreme two outliers from Il Sole
  ggplot(aes(x=subscribersCount)) +
  geom_histogram()+facet_wrap(~groupId, scales = "free")

subset_mum  %>% filter(subscribersCount<400000) %>% 
  ggplot(aes(y=subscribersCount, x=groupId))+geom_boxplot()+coord_flip()+
  geom_hline(yintercept=5000, linetype="dashed", color = "red", size=1)+
  geom_hline(yintercept=20000, linetype="dashed", color = "blue", size=1)

## Il Sole's account has higher number of followers than the other two but fewer outliers.
## Removing only the top 1% (extreme outliers) for Il Sole and Infobae but using followers for futher reducing Sky accounts.
## For Sky News, removing bottom 1% and top 15%. 
subset_mum %>% group_by(groupId) %>% summarise(meanSub=mean(subscribersCount), 
                                               maxSub=max(subscribersCount),
                                               minSub=min(subscribersCount),
                                               top1=quantile(subscribersCount, 0.99),
                                               top10=quantile(subscribersCount, 0.85),
                                               bottom5=quantile(subscribersCount, 0.01))


subset_mum %>% filter(groupId=="kids-sole" & postsCount>=144 &postsCount<=4595 & subscribersCount<=398064) %>% 
  rbind(subset_mum %>% filter(groupId=="kids-infobae" & postsCount>=189 &postsCount<=3099 & subscribersCount<=65107)
) %>% rbind(subset_mum %>% filter(groupId=="kids-sky-news" & postsCount>200 &postsCount<4031 & subscribersCount>=5069 & subscribersCount<=23692)) %>% 
  group_by(groupId) %>% summarise(accounts=n(), posts=sum(postsCount)) #%>% summarise(sum(accounts), sum(posts))

## Total number of accounts 896 and total number of posts 689,263.
## If collecting 100 posts per account, 89,600 posts.

# Subsetting original dataset based on conditions described above. 

newlist_scrapingIG=subset_mum %>% filter(groupId=="kids-sole" & postsCount>=144 &postsCount<=4595 & subscribersCount<=398064) %>% 
  rbind(subset_mum %>% filter(groupId=="kids-infobae" & postsCount>=189 &postsCount<=3099 & subscribersCount<=65107)
  ) %>% rbind(
    subset_mum %>% filter(groupId=="kids-sky-news" & postsCount>200 &postsCount<4031 & subscribersCount>=5069 & subscribersCount<=23692))

write.csv(newlist_scrapingIG, "newlist_scrapingIG.csv")
