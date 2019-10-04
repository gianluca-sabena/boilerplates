package main

import "fmt"

func main() {
	v := 10
	p := &v // get pointer to v
	fmt.Println("Value: ", v, "Pointer: ", p, "Value trought pinter: ", *p)
	*p = 20 // update value through the pointer p "dereferencing" or "indirecting"
	fmt.Println("Value: ", v, "Pointer: ", p, "Value trought pinter: ", *p)

}
