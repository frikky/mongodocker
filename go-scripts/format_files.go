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

func downloadFile(url, filename string) {
	resp, _ := http.Get(url)
	//check(err)

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

func getRegex(stringType string) string {
	if stringType == "ip" {
		return `(([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\.){3}([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])`
	} else if stringType== "md5" {
		return `^([a-f0-9]{32})$`
	} else if stringType == "sha256" {
		return `^([A-Fa-f0-9]{64})$`
	}  

	return "false"
}

func checkElementType(data string) (string, error) {	
	// Should compile inbetween to save resources
	ip_re, _ := regexp.Compile(getRegex("ip"))

	if ip_re.MatchString(data) {
		return "ip", nil
	}

	md5_re, _ := regexp.Compile(getRegex("md5"))
	// MD5 check
	if md5_re.MatchString(data) {
		return "MD5", nil
	} 

	sha256_re, _ := regexp.Compile(getRegex("sha256"))
	// Sha256 check
	if sha256_re.MatchString(data) {
		return "sha256", nil
	}

	return "", errors.New("Can't find matching object")
}

// Regex checks a loop
func regexMatchCheck(data string) string {
	var dataType string = ""
	for _, element := range strings.Split(data, "\n") {
		ret, _ := checkElementType(element)
		if ret == "" {
			continue
		}

		dataType = ret
		break
	}

	return dataType
}

func findVariableLocation(data string, regexType string) (int, string) {
	// Split type shoud be able to change
	splitType := ","
	var splitLocation = -1

	regex_setup, err := regexp.Compile(getRegex(regexType))
	check(err)
	
	for _, element := range strings.Split(data, "\n") {
		for count, subelement := range strings.Split(element, splitType) {
			if regex_setup.MatchString(subelement) {
				splitLocation = count						
				break
			}
		}

		if splitLocation >= 0 {
			break
		}
	}

	return splitLocation, splitType

}

// CSV check
func check_n_argument(data string) ([]string, error) {
	var dataList []string

	// Finds what kind of regex
	dataType := regexMatchCheck(data)
	if dataType == "" {
		return dataList, errors.New("No matching regex")
	}
	
	// Finds location to split on and type of split
	locationNumber, splitType := findVariableLocation(data, dataType)

	// Creates the actual list
	for _, element := range strings.Split(data, "\n") {
		if strings.HasPrefix(element, "#") || len(element) < 3 { 
			continue
		}

		dataList = append(dataList, strings.Split(element, splitType)[locationNumber])
	}

	// FIX - change from join
	return dataList, nil

}

// Should return domain, tld and download path 
func findURLInfo(data string) (string, string) {
	// FIX - checks type
	splitPos := 0
	firstSlashPos := 0
	lastSlashPos := 0
	var domain string
	var filename string

	if strings.HasPrefix(data, "http://") {
		splitPos = 7
		//domain = data[7:]
	} else if strings.HasPrefix(data, "https://") {
		splitPos = 8
	}

	for pos, char := range data {
		if fmt.Sprintf("%c", char) == "/" {
			if pos > splitPos && firstSlashPos <= 0{
				firstSlashPos = pos	
			}

			lastSlashPos = pos
		}

		if pos > splitPos {
		}
	}
	
	if firstSlashPos > 0 {
		domain = data[splitPos:firstSlashPos]
	} else {
		domain = data[splitPos:]
	}

	if splitPos > 0 {	
		filename = data[lastSlashPos+1:]
	} else {
		filename = data
	}

	return domain, filename
}

func main() {
	_, filename := findURLInfo(os.Args[1])
	//fmt.Println(domain, filename)

	// Verifies if a file actually exists.
	if len(os.Args) < 2 {
		fmt.Printf("Usage: go run %s <url>", "bambenek.go")
		os.Exit(3)
	}

	if checkFileExists(filename) == false {

		// Testurl: "http://osint.bambenekconsulting.com/feeds/c2-ipmasterlist-high.txt"
		url:= os.Args[1]
		fmt.Printf("Downloading file from %s\n", url)
		downloadFile(url, filename)
	}

	fmt.Printf("Attempting to parse file %s\n", filename)
	data := getData(filename)

	data_array, err := check_n_argument(data)	
	check(err)
	fmt.Printf("%s", data_array)
}
