package readwrite

import (
	"bufio"
	"os"
	"pr/fcacomponents"
	"strconv"
	"strings"
)

/*
Function that reads a .cxt file and returns a Context struct
*/
func Read_ctx(input_file string) fcacomponents.Context {
	var num_objects int
	var num_attributes int

	objects := fcacomponents.NewSet() // *Set, map allocated
	attributes := fcacomponents.NewSet()

	var cross_table [][]bool

	file, err := os.Open(input_file)
	check(err)
	defer file.Close()

	scanner := bufio.NewScanner(file)

	scanner.Scan()
	if scanner.Text() != "B" {
		panic(err)
	}
	scanner.Scan() // read the blank line

	scanner.Scan()
	num_objects, err = string_to_int(scanner.Text())
	check(err)

	scanner.Scan()
	num_attributes, err = string_to_int(scanner.Text())
	check(err)

	scanner.Scan() // read the blank line

	for indx := 0; indx < num_objects; indx++ {
		scanner.Scan()
		objects.Add(strings.Trim(scanner.Text(), "\n, "))
	}

	for indx := 0; indx < num_attributes; indx++ {
		scanner.Scan()
		attributes.Add(strings.Trim(scanner.Text(), "\n, "))
	}

	for i := 0; i < num_objects; i++ {
		scanner.Scan()
		entire_line := strings.Trim(scanner.Text(), "\n")

		if len(entire_line) != num_attributes { // ensure sizing is correct
			panic(err)
		}

		cross_table = append(cross_table, string_to_bool(entire_line))
	}

	return fcacomponents.Context{
		Objects:    *objects,
		Attributes: *attributes,
		Relation:   cross_table,
	}
}

func string_to_bool(input_str string) []bool {
	var return_val []bool

	for _, c := range input_str {
		if c == '1' || string(c) == "True" || c == 'X' {
			return_val = append(return_val, true)
		} else {
			return_val = append(return_val, false)
		}
	}
	return return_val
}

func string_to_int(input_str string) (int, error) {
	var ws = strings.TrimSpace(input_str)
	return (strconv.Atoi(ws))
}

func check(e error) {
	if e != nil {
		panic(e)
	}
}
