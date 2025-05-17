package fcacomponents

import (
	"strings"
)

type Implication struct {
	Premise    []string
	Conclusion []string
}

type Satisfaction interface {
	Satisfies() bool
}

func (c *Context) Satisfies(i *Implication) bool {
	premIdx := make([]int, len(i.Premise))
	for k, n := range i.Premise {
		premIdx[k] = c.a2i[n]
	}

	extPrem := append([]uint64(nil), c.cols[premIdx[0]]...)
	for _, a := range premIdx[1:] {
		col := c.cols[a]
		for w := range extPrem {
			extPrem[w] &= col[w]
		}
	}

	conIdx := make([]int, len(i.Conclusion))
	for k, n := range i.Conclusion {
		conIdx[k] = c.a2i[n]
	}

	extCon := append([]uint64(nil), c.cols[conIdx[0]]...)
	for _, a := range conIdx[1:] {
		col := c.cols[a]
		for w := range extCon {
			extCon[w] &= col[w]
		}
	}

	for w := range extPrem {
		if extPrem[w]&^extCon[w] != 0 {
			return false
		}
	}
	return true
}

func (i *Implication) String() string {
	var b strings.Builder
	b.WriteString(strings.Join(i.Premise, ", "))
	b.WriteString("->")
	b.WriteString(strings.Join(i.Conclusion, ", "))
	return b.String()
}
