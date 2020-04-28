package main

import (
	"fmt"
	"rsc.io/quote"
	"github.com/you/hello/msg"
)

func main() {
	fmt.Println(quote.Hello())
	fmt.Println(msg.HelloMessage())
}