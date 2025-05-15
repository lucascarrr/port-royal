package fcacomponents

import (
	"strings"
)

type Context struct {
	Objects    Set
	Attributes Set
	Relation   [][]bool
}

func (s Set) String() string {
	var b strings.Builder
	setlist := s.List()

	for key := range setlist {
		b.WriteString(setlist[key])
		b.WriteString(", ")
	}
	return b.String()
}

func (i Implication) String() string {
	var b strings.Builder
	b.WriteString(string(i.Premise.String()))
	b.WriteString("-> ")
	b.WriteString(string(i.Conclusion.String()))

	return b.String()
}

func (c Context) String() string {
	/* Instantiation of String() method for Stringer interface.
	Returns the string representation of a context
	*/
	var b strings.Builder
	maxAttrLen := 0
	for _, attr := range c.Attributes.List() {
		if len(attr) > maxAttrLen {
			maxAttrLen = len(attr)
		}
	}

	maxObjectLen := 0
	for _, attr := range c.Objects.List() {
		if len(attr) > maxAttrLen {
			maxObjectLen = len(attr)
		}
	}

	colObjWidth := maxObjectLen + 2
	colWidth := maxAttrLen + 2

	b.WriteString(strings.Repeat(" ", colObjWidth))
	b.WriteString("|")

	for _, attr := range c.Attributes.List() {
		b.WriteString(strings.Repeat(" ", (colWidth-len(attr))/2))
		b.WriteString(attr)
		b.WriteString(strings.Repeat(" ", (colWidth-len(attr)+1)/2))
		b.WriteString("|")
	}
	b.WriteString("\n")

	b.WriteString(strings.Repeat("–", colObjWidth+1))
	for range c.Attributes.List() {
		b.WriteString(strings.Repeat("–", colWidth+1))
	}
	b.WriteString("\n")

	for i, obj := range c.Objects.List() {
		b.WriteString(obj)
		b.WriteString(strings.Repeat(" ", colObjWidth-len(obj)))
		b.WriteString("|")
		for j := range c.Attributes.List() {
			if c.Relation[i][j] {
				b.WriteString(strings.Repeat(" ", colWidth/2))
				b.WriteString("X")
				b.WriteString(strings.Repeat(" ", colWidth/2))
				b.WriteString("|")
			} else {
				b.WriteString(strings.Repeat(" ", colWidth/2))
				b.WriteString(" ")
				b.WriteString(strings.Repeat(" ", colWidth/2))
				b.WriteString("|")
			}
		}
		b.WriteString("\n")
	}

	return b.String()
}

type Derivation interface {
	Derive()
}

type Implication struct {
	Premise    Set
	Conclusion Set
}

type Consequence interface {
	Satisfies() bool
}

func (s Set) Satisfies(i Implication) bool {
	satisfies_conclusion, _ := s.Subseteq(&i.Conclusion)

	if satisfies_conclusion {
		return true
	}

	satisfies_premise, _ := s.Subseteq(&i.Premise)
	return !satisfies_premise
}
