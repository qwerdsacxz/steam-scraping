#!/usr/bin/env python
# coding: utf-8

# In[2]:


import pandas as pd
import jieba
f=open('标签.txt','r',encoding='utf-8')
content=f.read()
f.close()
print(content)


# In[3]:


words=jieba.lcut(content)
count={}
for word in words:
    if len(word) == 1:
        continue
    else:
        count[word]=count.get(word,0)+1
print(count)


# In[4]:


items=list(count.items())
items.sort(key=lambda x:x[1],reverse=True)
items


# In[35]:


save = pd.DataFrame(items,columns = ['word','times'])
save.to_excel('标签.xlsx')


# In[ ]:




