package fcacomponents

import (
	"fmt"
	"math/bits"
	"strings"
)

type Context struct {
	Objects    []string       // index → name
	Attributes []string       // index → name
	o2i        map[string]int // name → index
	a2i        map[string]int // name → index
	cols       [][]uint64     // attribute j → bitset over objects
	words      int            // cached: len(cols[j])
}

func NewContext(objects, attrs []string, incidence [][2]string) (*Context, error) {
	c := &Context{
		Objects:    objects,
		Attributes: attrs,
		o2i:        make(map[string]int, len(objects)),
		a2i:        make(map[string]int, len(attrs)),
	}
	for indx, obj := range objects {
		c.o2i[obj] = indx
	}

	for jndx, attr := range attrs {
		c.a2i[attr] = jndx
	}

	c.words = (len(objects) + 63) >> 6
	c.cols = make([][]uint64, len(attrs))

	for j := range c.cols {
		c.cols[j] = make([]uint64, c.words)
	}

	for _, pair := range incidence {
		obj := pair[0]
		attr := pair[1]
		obj_indx, err := c.o2i[obj]

		if !err {
			return c, fmt.Errorf("unknown object %q", obj)
		}

		attr_indx, err := c.a2i[attr]
		if !err {
			return c, fmt.Errorf("unknown attribute %q", attr)
		}

		w, b := obj_indx>>6, uint(obj_indx&63)

		c.cols[attr_indx][w] |= 1 << b
	}

	return c, nil
}

func (c *Context) AddIncidence(object, attribute string) error {
	obj, err := c.o2i[object]

	if !err {
		return fmt.Errorf("unknown object %q", object)
	}

	attr, err := c.a2i[attribute]
	if !err {
		return fmt.Errorf("unknown attribute %q", attribute)
	}

	w, b := obj>>6, uint(obj&63)

	c.cols[attr][w] |= 1 << b
	return nil
}

func (c *Context) Extent(attrNames []string) []string {
	if len(attrNames) == 0 {
		return append([]string(nil), c.Objects...)
	}

	ids := make([]int, len(attrNames)) // slice containing all id-bits for attributes in argument
	for k, n := range attrNames {
		ids[k] = c.a2i[n] // given an attribute name (string) we assign the id-bit
	}

	res := append([]uint64(nil), c.cols[ids[0]]...) // copy the slice

	for _, a := range ids[1:] {
		col := c.cols[a]
		for w := range res {
			res[w] &= col[w] // bitwise AND
		}
	}
	return c.objsFromBits(res)
}

func (c *Context) Intent(objNames []string) []string {
	if len(objNames) == 0 {
		return append([]string(nil), c.Attributes...)
	}

	objIDs := make([]int, len(objNames))
	for k, n := range objNames {
		objIDs[k] = c.o2i[n]
	}

	intent := make([]string, 0, len(c.Attributes))
checkAttr:
	for a, col := range c.cols {
		for _, o := range objIDs {
			w, b := o>>6, uint(o&63)
			if (col[w]>>b)&1 == 0 {
				continue checkAttr
			}
		}
		intent = append(intent, c.Attributes[a])
	}
	return intent
}

// objsFromBits converts a bitmap to a slice of object names.
func (c *Context) objsFromBits(bitslice []uint64) []string {
	out := make([]string, 0)
	for wordIdx, word := range bitslice {
		for word != 0 {
			tz := bits.TrailingZeros64(word)
			objID := (wordIdx << 6) + tz
			if objID < len(c.Objects) { // mask in last partial word
				out = append(out, c.Objects[objID])
			}
			word &= word - 1 // clear lowest-set bit
		}
	}
	return out
}

// PopcountObjects returns |S| for a set S of objects given as a bitset.
func PopcountObjects(bitslice []uint64) int {
	var n int
	for _, w := range bitslice {
		n += bits.OnesCount64(w)
	}
	return n
}

func (c *Context) String() string {
	var b strings.Builder

	maxAttrLen := 0
	for _, attr := range c.Attributes {
		if len(attr) > maxAttrLen {
			maxAttrLen = len(attr)
		}
	}

	maxObjectLen := 0
	for _, obj := range c.Objects {
		if len(obj) > maxObjectLen {
			maxObjectLen = len(obj)
		}
	}

	colObjWidth := maxObjectLen + 2
	colWidth := maxAttrLen + 2

	// header row
	b.WriteString(strings.Repeat(" ", colObjWidth))
	b.WriteString("|")
	for _, attr := range c.Attributes {
		padding := (colWidth - len(attr)) / 2
		b.WriteString(strings.Repeat(" ", padding))
		b.WriteString(attr)
		b.WriteString(strings.Repeat(" ", colWidth-len(attr)-padding))
		b.WriteString("|")
	}
	b.WriteString("\n")

	// divider row
	b.WriteString(strings.Repeat("–", colObjWidth+1))
	for range c.Attributes {
		b.WriteString(strings.Repeat("–", colWidth+1))
	}
	b.WriteString("\n")

	// body rows
	for _, obj := range c.Objects {
		b.WriteString(obj)
		b.WriteString(strings.Repeat(" ", colObjWidth-len(obj)))
		b.WriteString("|")

		obj_id := c.o2i[obj]
		for _, attr := range c.Attributes {
			attr_id := c.a2i[attr]
			word := obj_id >> 6
			bit := uint(obj_id & 63)
			has := (c.cols[attr_id][word]>>bit)&1 == 1

			padding := colWidth / 2
			b.WriteString(strings.Repeat(" ", padding))
			if has {
				b.WriteString("X")
			} else {
				b.WriteString(" ")
			}
			b.WriteString(strings.Repeat(" ", colWidth-padding-1))
			b.WriteString("|")
		}
		b.WriteString("\n")
	}

	return b.String()
}
