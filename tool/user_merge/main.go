package main

import (
	"database/sql"
	"fmt"
	"log"

	_ "github.com/go-sql-driver/mysql" // 导入 MySQL 驱动
)

func main() {
	// 数据库连接信息
	dsn := "username:password@tcp(127.0.0.1:3306)/database_name"

	// 打开数据库连接
	db, err := sql.Open("mysql", dsn)
	if err != nil {
		log.Fatalf("连接数据库失败: %v", err)
	}
	defer db.Close()

	// 测试连接
	err = db.Ping()
	if err != nil {
		log.Fatalf("无法连接到数据库: %v", err)
	}

	fmt.Println("成功连接到 MySQL 数据库！")
}
