# Kokomi 用户数据库设计

## Region数据

### Table 1: Region

用于储存id对应的地区（主要是为了减少数据库大小）， 内连后续表

```sql
CREATE TABLE region (
    region_id      TINYINT        NOT NULL,
    region_str     VARCHAR(5)     NOT NULL,

    PRIMARY KEY (region_id)
);

INSERT INTO region 
    (region_id, region_str) 
VALUES
    (1, "asia"), (2, "eu"), (3, "na"), (4, "ru"), (5, "cn");
```

#### region_id对应列表

| region_id | region_str |
| --------- | ---------- |
| 1         | asia       |
| 2         | eu         |
| 3         | na         |
| 4         | ru         |
| 5         | cn         |
