package main

import (
	"fmt"
	"strings"
)

func WordCount(s string) map[string]int {
	var m map[string]int
	m = make(map[string]int)
	for _, s := range strings.Fields(s) {
		m[s] = m[s] + 1
	}
	//fmt.Print(m)
	return m
}

func main() {
	fmt.Println(WordCount("Hello world !"))
}
