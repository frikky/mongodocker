package main

import (
	"fmt"
	"os"
	"net/http"
	"io/ioutil"
)

func check(e error) {
	if e != nil {
		panic(e)
	}
}

func checkFileExists(path string) bool {
	if _, err := os.Stat(path); err != nil {
		if os.IsNotExist(err) {
			return false
		}
	}
	return true
}

func createFile(url, filename string) {
	resp, err := http.Get(url)
	check(err)

	if err != nil {
		// handle error
	}

	defer resp.Body.Close()
	bodyBytes, err := ioutil.ReadAll(resp.Body)
	check(err)

	fmt.Println("File doesn't exist")
	ioutil.WriteFile(filename, bodyBytes, 0664)
	check(err)
}

func getData(filename string) string {
	b, err := ioutil.ReadFile(filename)
	check(err)

	str := string(b) 
	return str
}

func main() {
	filename := "ip"

	// Verifies if a file actually exists.
	if checkFileExists(filename) == false {
		url := "http://osint.bambenekconsulting.com/feeds/c2-ipmasterlist-high.txt"
		createFile(url, filename)
	}

	data := getData(filename)
	fmt.Println(data)
}
