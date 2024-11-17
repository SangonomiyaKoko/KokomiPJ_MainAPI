# MySQL 存储过程设计

## User 表

### 1. 用户是否存在检测

SQL 语句

```sql
DELIMITER $$

CREATE PROCEDURE insert_or_get_user(IN p_account_id INT, IN p_region_id INT, IN p_default_name VARCHAR(255), OUT p_username VARCHAR(255))
BEGIN
    -- 查询是否存在记录
    SELECT username INTO p_username
    FROM user_basic
    WHERE region_id = p_region_id AND account_id = p_account_id;

    -- 如果不存在则插入默认值并初始化其他表
    IF p_username IS NULL THEN
        SET p_username = p_default_name;
        INSERT INTO user_basic (account_id, region_id, username) VALUES (p_account_id, p_region_id, p_username);
        INSERT INTO user_info (account_id) VALUES (p_account_id);
        INSERT INTO user_pr (account_id) VALUES (p_account_id);
        INSERT INTO user_ships (account_id) VALUES (p_account_id);
    END IF;
END$$

DELIMITER ;
```

调用示例

```sql
CALL insert_or_get_user(2023619512, 1, 'User_2023619512', @username);
SELECT @username AS name;
```
