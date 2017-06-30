package main

import (
	"fmt"
	"os"
	"regexp"
	"errors"
	"strings"
	"net/http"
	"io/ioutil"
)

/*
type argError struct {
	arg  int
	prob string
}
*/

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

func check_element_type(data string) (string, error) {	
	// Should compile inbetween to save resources
	ip_re, _ := regexp.Compile(`^(([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\.){3}([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])$`)

	// FIX - Hash not tested
	if ip_re.MatchString(data) {
		return "ip", nil
	}

	// MD5 check
	md5_re, _ := regexp.Compile(`^([a-f0-9]{32})$`)
	if md5_re.MatchString(data) {
		return "MD5", nil
	} 

	// Sha256 check
	sha256_re, _ := regexp.Compile(`^([A-Fa-f0-9]{64})$`)
	if sha256_re.MatchString(data) {
		return "sha256", nil
	}

	return "", errors.New("Can't find matching object")
}

// CSV check
func check_n_argument(n int, data string) ([]string, error) {
	var datalist []string

	for _, element := range strings.Split(data, "\n") {
		// Removes newlines/emptystrings and startswith(hash)
		if strings.HasPrefix(element, "#") || len(element) < 3 { 
			continue
		}

		// Verify if actually IP, hash, url or similar here
		argument := strings.Split(element, ",")[n]

		// Continue if "None"
		_, error := check_element_type(argument)
		check(error)

		datalist = append(datalist, argument)
	}

	if len(datalist) <= 0 {
		return nil, errors.New("No arguments matching regex found.")	
	}

	// FIX - change from join
	return datalist, nil

}

func main() {
	filename := "ip"

	// Verifies if a file actually exists.
	if checkFileExists(filename) == false {
		// Testurl: "http://osint.bambenekconsulting.com/feeds/c2-ipmasterlist-high.txt"
		url := os.Args[1]
		createFile(url, filename)
	}

	data := getData(filename)

	// Makes it check first argument first. (CSV) 
	data_array, err := check_n_argument(0, data)	
	check(err)
	fmt.Printf("\n%s", data_array)
}
