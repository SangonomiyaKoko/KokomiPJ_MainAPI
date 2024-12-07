# 战舰世界游戏接口文档

## Official API

此接口是游戏官方提供给开发者的官方接口，用户注册授权后才可使用，需要遵循相关的[用户协议](https://developers.wargaming.net/documentation/rules/agreement/)

> 条款内的内容非常重要，请务必在使用前阅读一遍以避免可能的潜在的法律麻烦

```txt
7. WHAT THE API MUST NOT BE USED FOR

—— makes any private information on the Platform publicly available on the Application;
—— observe, study or test the functioning of the API (or any part of it) beyond the limits reasonably required to develop Your Applications;

......

9. API LICENSEE’S RIGHTS TO USE THE API DATA AND OTHER CONTENT

—— you shall not create permanent copies of the API Data;
—— you shall not without Our prior written consent, make derivative works of, or commercially distribute or otherwise exploit the API Data
```

Wargaming 接口地址: <https://developers.wargaming.net/>

LestaGame 接口地址: 忘了(

> **注意，由于 360Game 并没有提供这个接口，所以国服很多功能无法实现**

## Vortex API

此接口为游戏客户端接口，使用时不需要授权，相较于官方提供的接口可以获取更多的数据，**且所有服务器均支持该接口**

关于每个服务器对应接口的 url 如下:

```python
VORTEX_API_URL_LIST = {
    1: 'http://vortex.worldofwarships.asia',
    2: 'http://vortex.worldofwarships.eu',
    3: 'http://vortex.worldofwarships.com',
    4: 'http://vortex.korabli.su',
    5: 'http://vortex.wowsgame.cn'
}
```

> 以下接口示例均以亚服我自己账号的为例，您可以修改为自己的 id 来测试

### 用户搜索接口 1

```url
GET https://vortex.worldofwarships.asia/api/accounts/search/autocomplete/kokomi123/
```

注意: 360Game 不支持该接口，请使用下面的接口

### 用户搜素接口 2

```url
GET http://vortex.worldofwarships.asia/api/accounts/search/kokomi123/?limit=10
```

### 获取船只信息数据

```url
GTE http://vortex.worldofwarships.asia/api/encyclopedia/en/vehicles/
```

### 获取服务器当前版本

```url
POST https://vortex.worldofwarships.asia/api/v2/graphql/glossary/version/

[{"query":"query Version {\n  version\n}"}]
```

### 获取用户基本数据

```url
GET http://vortex.worldofwarships.asia/api/accounts/2023619512/
```

### 获取用户所在工会

```url
GET http://vortex.worldofwarships.asia/api/accounts/2023619512/clans/
```

### 获取用户的成就数据

```url
GET http://vortex.worldofwarships.asia/api/accounts/2023619512/achievements/
```

### 获取用户船只的简略信息

```url
GET http://vortex.worldofwarships.asia/api/accounts/2023619512/ships/
```

### 获取用户船只的指定类型的信息

```url
GET http://vortex.worldofwarships.asia/api/accounts/2023619512/ships/pve/
GET http://vortex.worldofwarships.asia/api/accounts/2023619512/ships/pvp/
GET http://vortex.worldofwarships.asia/api/accounts/2023619512/ships/pvp_solo/
GET http://vortex.worldofwarships.asia/api/accounts/2023619512/ships/pvp_div2/
GET http://vortex.worldofwarships.asia/api/accounts/2023619512/ships/pvp_div3/
GET http://vortex.worldofwarships.asia/api/accounts/2023619512/ships/rank_solo/
GET http://vortex.worldofwarships.asia/api/accounts/2023619512/ships/rank_div2/
GET http://vortex.worldofwarships.asia/api/accounts/2023619512/ships/rank_div3/
```

### 获取用户指定船只的指定类型的信息

```url
GET http://vortex.worldofwarships.asia/api/accounts/2023619512/ships/4285445840/pve/
...... 后续参数同上
```

## Other API

该部分接口主要来自游戏相关网站的接口，例如兵工厂和工会

### 工会搜索接口

```url
GET http://vortex.worldofwarships.asia/api/search/autocomplete/?search=TIF-K&type=clans
```
