package main

import (
	"fmt"
	"pr/fcacomponents"
	"pr/readwrite"
	"strings"
)

func main() {
	cxt := readwrite.ParseJSON("contexts/friends.json")
	fmt.Println(cxt)
	fmt.Println("The extent of \"fw. charlie\" is:", strings.Join(cxt.Extent([]string{"fw. charlie"}), ", "))
	impl1 := fcacomponents.Implication{[]string{"fw. charlie"}, []string{"fw. bob"}}
	fmt.Println("The implication", impl1.String(), "is", cxt.Satisfies(&impl1))

}
