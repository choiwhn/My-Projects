#!/usr/bin/env python
# coding: utf-8

# # 0. input data

# In[1]:


day = int(input('day?: '))
time = input('time?: ')
code_int=input('code?: ')


# In[2]:


alpha=float(input('truncation coeff?(0 ~ 1): '))


# # 1.0 stay data

# In[3]:


import pandas as pd
import numpy as np


# In[4]:


import data_rev
from preprocessing_pkg.stay import stay


# In[5]:


df=data_rev.df_revised
df.head()


# In[6]:


df2=stay(day, time)


# In[7]:


df2['hdong_cd'] = df2['hdong_cd'].astype(str)
df = pd.merge(df, df2, left_on='code', right_on='hdong_cd', how='inner')
df = df.drop(columns=['hdong_cd'])
df = df.rename(columns={'stay_cnts': 'pop'})
df.head()


# In[8]:


seoularea=pd.read_csv('data/seoularea.csv')
seoularea=seoularea[['행정동코드','면적']]
seoularea.columns=['code','area']
seoularea.head()


# In[9]:


sc=150000


# In[10]:


df['pop'] = df["pop"].fillna(0)
df['scaled_pop']=df['pop'] / sc  ##scale parameter
df['area']=seoularea['area']
df['pop_density']=df['pop']/df['area']
df['scaled_pop_density']=df['pop'] / sc
df.head()


# # 2.0 od data

# In[11]:


#central lon, lat 계산
coordinates=df['coordinates'].to_numpy()
lon = np.zeros(426);lat = np.zeros(426)
for i in range(426):
    lonlat=np.mean(coordinates[i],axis=0)
    lon[i],lat[i]=lonlat[0],lonlat[1]


# In[12]:


df['lat']=lat
df['lon']=lon
df1=df[['code','lat','lon']]
df1.head()


# In[13]:


arr=df1.to_numpy()
arr_ft=np.zeros((426*426,6))
for i,f in enumerate(arr):
    for j,t in enumerate(arr):
        arr_ft[i*426+j]=np.hstack((f,t))


# In[14]:


#관심 행정동 코드
other_coord=list()
for i in arr:
    if i[0]!=code_int: other_coord.append(i)
    else: coordlst=i


# In[15]:


coord=coordlst
for i in range(425-1):
    coord=np.vstack((coord,coordlst))


# In[16]:


arr_in=np.hstack((other_coord,coord))
arr_out=np.hstack((coord,other_coord))


# In[17]:


df_in=pd.DataFrame(arr_in)
df_in.columns = ['from','from_lat','from_lon','to','to_lat','to_lon']
df_in.head()


# In[18]:


df_out=pd.DataFrame(arr_out)
df_out.columns = ['from','from_lat','from_lon','to','to_lat','to_lon']
df_out.head()


# In[19]:


def trunc(data,alpha): #alpha is truncation constant: data < alpha => data = 0
    data=data.to_numpy()
    data=data.copy()
    for i in range(len(data)):
        if data[i]-alpha<0: data[i]=0
    return data


# In[20]:


from preprocessing_pkg.od import od_in, od_out


# In[21]:


in_pop = od_in(date=day, end_time=time, dest=code_int, from_seoul=True)

df_in = pd.merge(df_in, in_pop, how="left", left_on="from", right_on="origin_hdong_cd")
del df_in["origin_hdong_cd"]
df_in.rename(columns={"od_cnts": "pop"}, inplace=True)


# In[22]:


sc=150


# In[23]:


df_in['pop'] = df_in['pop'].fillna(0)
df_in['scaled_pop']=df_in['pop'] / sc
df_in['trunc_scaled_pop']=trunc(df_in['scaled_pop'],alpha)
df_in.head()


# In[24]:


out_pop = od_out(date=day, start_time=time, origin=code_int, to_seoul=True)
df_out = pd.merge(df_out, out_pop, how="left", left_on="to", right_on="dest_hdong_cd")
del df_out["dest_hdong_cd"]
df_out.rename(columns={"od_cnts": "pop"}, inplace=True)


# In[25]:


df_out['pop'] = df_out["pop"].fillna(0)
df_out['scaled_pop']=df_out['pop'] / sc
df_out['trunc_scaled_pop']=trunc(df_out['scaled_pop'],alpha)
df_out.head()


# In[26]:


def plus(data):
    data=data.to_numpy()
    data=data.copy()
    for i in range(len(data)):
        if data[i]<0: data[i]=0
    return data

def minus(data): 
    data=data.to_numpy()
    data=data.copy()
    for i in range(len(data)):
        if data[i]>0: data[i]=0
    return -1*data


# In[27]:


df_diff=df_in[['from','from_lat','from_lon','to','to_lat','to_lon']].copy()
df_diff['pop'] = df_in['pop']-df_out['pop']
df_diff['scaled_pop']=df_diff['pop'] / sc
df_diff['scaled_pop_p']=plus(df_diff['scaled_pop'])
df_diff['scaled_pop_m']=minus(df_diff['scaled_pop'])
df_diff['trunc_scaled_pop']=trunc(abs(df_diff['scaled_pop']),alpha)
df_diff['abs_scaled_pop']=abs(df_diff['scaled_pop'])
df_diff['trunc_abs_scaled_pop']=abs(df_diff['trunc_scaled_pop'])
df_diff.head()

