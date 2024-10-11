#!/usr/bin/env python
# coding: utf-8

# # 0. input data

# In[ ]:


day = input('day?: ')
time = input('time?: ')
code_int=input('code?: ')


# In[ ]:


alpha=float(input('truncation coeff?(0 ~ 1): '))


# # 1.0 stay data

# In[ ]:


import pandas as pd
import numpy as np


# In[ ]:


import data_rev


# In[ ]:


df=data_rev.df_revised
df.head()


# In[ ]:


df['pop'] = np.random.exponential(10,426)###data to be merged
df['nor_pop']=df['pop'] / df['pop'].max()
#pop_density, #nor_pop_density
df.head()


# # 2.0 od data

# In[ ]:


#central lon, lat
coordinates=df['coordinates'].to_numpy()
lon = np.zeros(426);lat = np.zeros(426)
for i in range(426):
    lonlat=np.mean(coordinates[i],axis=0)
    lon[i],lat[i]=lonlat[0],lonlat[1]


# In[ ]:


df['lat']=lat
df['lon']=lon
df1=df[['code','lat','lon']]
df1.head()


# In[ ]:


arr=df1.to_numpy()
arr_ft=np.zeros((426*426,6))
for i,f in enumerate(arr):
    for j,t in enumerate(arr):
        arr_ft[i*426+j]=np.hstack((f,t))


# In[ ]:


#관심 행정동 코드
other_coord=list()
for i in arr:
    if i[0]!=code_int: other_coord.append(i)
    else: coordlst=i


# In[ ]:


coord=coordlst
for i in range(425-1):
    coord=np.vstack((coord,coordlst))


# In[ ]:


arr_in=np.hstack((other_coord,coord))
arr_out=np.hstack((coord,other_coord))


# In[ ]:


df_in=pd.DataFrame(arr_in)
df_in.columns = ['from','from_lat','from_lon','to','to_lat','to_lon']
df_in.head()


# In[ ]:


df_out=pd.DataFrame(arr_out)
df_out.columns = ['from','from_lat','from_lon','to','to_lat','to_lon']
df_out.head()


# In[ ]:


def trunc(data,alpha): #alpha is truncation constant: data < alpha => data = 0
    data=data.to_numpy()
    data=data.copy()
    for i in range(len(data)):
        if data[i]-alpha<0: data[i]=0
    return data


# In[ ]:


df_in['pop'] = np.random.exponential(10,425)###data to be merged
df_in['nor_pop']=df_in['pop'] / df_in['pop'].max()
df_in['trunc_nor_pop']=trunc(df_in['nor_pop'],alpha)
df_in.head()


# In[ ]:


df_out['pop'] = np.random.exponential(10,425)###data to be merged
df_out['nor_pop']=df_out['pop'] / df_out['pop'].max()
df_out['trunc_nor_pop']=trunc(df_out['nor_pop'],alpha)
df_out.head()


# In[ ]:


df_diff=df_in[['from','from_lat','from_lon','to','to_lat','to_lon']].copy()
df_diff['pop'] = df_in['pop']-df_out['pop']
df_diff['nor_pop']=df_diff['pop'] / abs(df_diff['pop']).max()
df_diff['trunc_nor_pop']=trunc(abs(df_diff['nor_pop']),alpha)
df_diff['abs_nor_pop']=abs(df_diff['nor_pop'])
df_diff['abs_trunc_nor_pop']=abs(df_diff['trunc_nor_pop'])
df_diff.head()

