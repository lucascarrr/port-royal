package readwrite

import (
	"encoding/json"
	"os"
	"pr/fcacomponents"
)

type RawContext struct {
	Objects    []string    `json:"objects"`
	Attributes []string    `json:"attributes"`
	Incidence  [][2]string `json:"incidence"`
}

func ParseJSON(filename string) *fcacomponents.Context {
	file, err := os.Open(filename)
	if err != nil {
		panic(err)
	}
	defer file.Close()

	var raw RawContext
	decoder := json.NewDecoder(file)
	err = decoder.Decode(&raw)
	if err != nil {
		panic(err)
	}

	ctx, err := fcacomponents.NewContext(raw.Objects, raw.Attributes, raw.Incidence)
	if err != nil {
		panic(err)
	}
	return ctx
}
