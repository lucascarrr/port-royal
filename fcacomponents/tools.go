package fcacomponents

// Set is a collection of unique elements
type Set struct {
	elements map[string]struct{}
}

func NewSet() *Set {
	// NewSet creates a new set
	return &Set{
		elements: make(map[string]struct{}),
	}
}

func (s *Set) Add(value string) {
	// Add inserts an element into the set
	s.elements[value] = struct{}{}
}

func (s *Set) Remove(value string) {
	// Remove deletes an element from the set
	delete(s.elements, value)
}

func (s *Set) Contains(value string) bool {
	// Contains checks if an element is in the set
	_, found := s.elements[value]
	return found
}

func (s *Set) Size() int {
	// Size returns the number of elements in the set
	return len(s.elements)
}

func (s *Set) List() []string {
	// Returns the set as a slice
	keys := make([]string, 0, len(s.elements))
	for key := range s.elements {
		keys = append(keys, key)
	}
	return keys
}

func (s *Set) Union(other *Set) *Set {
	// Returns the union of two sets as another set
	result := NewSet()
	for key := range s.elements {
		result.Add(key)
	}
	for key := range other.elements {
		result.Add(key)
	}
	return result
}

func (s *Set) Intersection(other *Set) *Set {
	// Returns the intersection of two sets as another set
	result := NewSet()
	for key := range s.elements {
		if other.Contains(key) {
			result.Add(key)
		}
	}
	return result
}

func (s *Set) Subseteq(other *Set) (bool, bool) {
	// Returns a pair (b1, b2) first item is true if other is a subset of s, second item is true if equality is true
	for key := range other.elements {
		if !s.Contains(key) {
			return false, false
		}
	}
	if s.Size() == other.Size() {
		return true, true
	}
	return true, false
}

func (s *Set) Difference(other *Set) *Set {
	// Returns the difference between two sets as another set
	result := NewSet()
	for key := range s.elements {
		if !other.Contains(key) {
			result.Add(key)
		}
	}
	return result
}
