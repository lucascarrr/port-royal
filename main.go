package main

import (
	"fmt"
	//"pr/fcacomponents"
	"pr/readwrite"
)

func main() {
	context := readwrite.Read_ctx("contexts/penguins.cxt")
	fmt.Println(context)
	/*
	   premise := fcacomponents.NewSet()
	   premise.Add("bird")

	   conclusion := fcacomponents.NewSet()
	   conclusion.Add("flies")

	   tester := fcacomponents.NewSet()
	   tester.Add("bird")
	   tester.Add("swims")

	   impl1 := fcacomponents.Implication{*premise, *conclusion}
	   fmt.Println(tester.Satisfies(impl1))
	   fmt.Println(impl1)
	*/
}
