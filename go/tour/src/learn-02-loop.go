package main

import (
	"fmt"
	"math"
)

// Sqrt ...
func Sqrt(x float64) float64 {
	z := 1.0
	for i := 0; i < 10; i++ {
		prev := z
		z -= (z*z - x) / (2 * z)
		fmt.Println(z)
		if math.Abs(prev-z) < math.Pow10(-6) {
			return z
		}
	}
	return z
}

func main() {
	fmt.Println(Sqrt(2))
}
