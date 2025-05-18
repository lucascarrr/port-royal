package fcacomponents

import (
	"strings"
)

type Implication struct {
	Premise    []string
	Conclusion []string
}

type Satisfaction interface {
	Satisfies() (bool, string)
}

func (c *Context) Satisfies(i *Implication) (bool, string) {
	var b strings.Builder
	b.WriteString(i.String())
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
			b.WriteString(" is not satisfied by the context")
			return false, b.String()
		}
	}
	b.WriteString(" is satisfied by the context")

	return true, b.String()
}

func (i *Implication) String() string {
	var b strings.Builder
	b.WriteString(strings.Join(i.Premise, ", "))
	b.WriteString("->")
	b.WriteString(strings.Join(i.Conclusion, ", "))
	return b.String()
}
