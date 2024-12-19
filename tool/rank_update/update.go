package main

import (
	"fmt"
	"net/http"
	"time"
)

func fetchData(url string) {
	resp, err := http.Post(url, "application/json", nil)
	if err != nil {
		fmt.Printf("Error fetching data: %v\n", err)
		return
	}
	defer resp.Body.Close()

	if resp.StatusCode == http.StatusOK {
		fmt.Println("Data updated successfully")
	} else {
		fmt.Printf("Failed to update data, status code: %d\n", resp.StatusCode)
	}
}

func main() {
	url := "http://127.0.0.1:8000/rank/update/"

	fmt.Println("Running fetchData for the first time...")
	fetchData(url)

	fmt.Println("Waiting for 60 minutes before the next update...")
	time.Sleep(60 * time.Minute)

	fmt.Printf("Start to update data every 60 minutes\n")
	ticker := time.NewTicker(60 * time.Minute)
	defer ticker.Stop()

	go func() {
		for {
			select {
			case <-ticker.C:
				fetchData(url)
			}
		}
	}()

	select {}
}