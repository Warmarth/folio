# Reference solutions (mentor only)

Every solution below passes all of its tests.

## Reverse a word (easy)

```go
package main

import "fmt"

func main() {
	var s string
	fmt.Scan(&s)
	r := []rune(s)
	for i, j := 0, len(r)-1; i < j; i, j = i+1, j-1 {
		r[i], r[j] = r[j], r[i]
	}
	fmt.Println(string(r))
}
```

## Even or odd (easy)

```go
package main

import "fmt"

func main() {
	var n int
	fmt.Scan(&n)
	if n%2 == 0 {
		fmt.Println("even")
	} else {
		fmt.Println("odd")
	}
}
```

## Count the vowels (medium)

```go
package main

import (
	"bufio"
	"fmt"
	"os"
	"strings"
)

func main() {
	scanner := bufio.NewScanner(os.Stdin)
	scanner.Scan()
	count := 0
	for _, c := range strings.ToLower(scanner.Text()) {
		if strings.ContainsRune("aeiou", c) {
			count++
		}
	}
	fmt.Println(count)
}
```

## Sum of a list (medium)

```go
package main

import "fmt"

func main() {
	var n, x, sum int
	fmt.Scan(&n)
	for i := 0; i < n; i++ {
		fmt.Scan(&x)
		sum += x
	}
	fmt.Println(sum)
}
```

## Most frequent word (hard)

```go
package main

import (
	"bufio"
	"fmt"
	"os"
)

func main() {
	scanner := bufio.NewScanner(os.Stdin)
	scanner.Split(bufio.ScanWords)
	counts := map[string]int{}
	for scanner.Scan() {
		counts[scanner.Text()]++
	}
	best, bestCount := "", 0
	for w, c := range counts {
		if c > bestCount || (c == bestCount && w < best) {
			best, bestCount = w, c
		}
	}
	fmt.Println(best)
}
```

