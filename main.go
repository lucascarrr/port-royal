package main

import (
	"fmt"
	"pr/fcacomponents"
	"pr/readwrite"
	"strings"
)

func main() {
	cxt := readwrite.ParseJSON("contexts/birds.json")
	fmt.Println(cxt)

	fmt.Println("The extent of \"bird\" is", strings.Join(cxt.Extent([]string{"bird"}), ", "))
	fmt.Println("The extent of \"flies\" is", strings.Join(cxt.Extent([]string{"flies"}), ", "))

	impl1 := fcacomponents.Implication{
		Premise:    []string{"bird"},
		Conclusion: []string{"flies"},
	}
	_, res := cxt.Satisfies(&impl1) // discard the first result
	fmt.Println(res)

	impl2 := fcacomponents.Implication{
		Premise:    []string{"bird"},
		Conclusion: []string{"wings"},
	}
	_, res1 := cxt.Satisfies(&impl2)
	fmt.Println(res1)
}
