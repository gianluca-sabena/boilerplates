package main

import (
	"fmt"

	"github.com/you/hello/msg"
	"rsc.io/quote"
)

func main() {
	fmt.Println(quote.Hello())
	fmt.Println(msg.HelloMessage())
}
