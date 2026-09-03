# 2024 AIME II Problem 2

A list of positive integers has the following properties:

$\bullet$ The sum of the items in the list is $30$.

$\bullet$ The unique mode of the list is $9$.

$\bullet$ The median of the list is a positive integer that does not appear in the list itself.

Find the sum of the squares of all the items in the list.

## Quick note

For those who don't understand why we say the list must have 4 elements.

Suppose there are $2n$ elements in the set. Then, the remaining $2n-2$ elements must sum to 12. So, say instead there were $2n=6$ elements in the set. Then, we need four integers that add to 12. However, the unique mode is 9, which appears twice. Thus, every other number must appear once. The smallest sum of four distinct numbers is $1+2+3+4=10$. To obtain 12, we sub out 4 for 6. However, now we have a problem! The median of the set isn't an integer. Thus, 6 elements cannot work.

Now, say there are $2n = 8$ elements. Like in the previous case, the unique mode is 9, which appears twice. Along with that fact, each number must be distinct. The smallest sum of $8-2=6$ numbers is 21, which is not even close to 12. Thus, we can conclude that as $2n \rightarrow \infty$, the distinct sum $S >> 12$ ($>>$ means much larger). Thus, the case of $2n=8$ doesn't work, and all cases of $2n > 8$ don't work.

So, we have either $2n = 2,4,6$, in which we know $2n \neq 2,6$, and therefore $2n$ must be 4, so there must be 4 elements in the set $\square$.

~Pinotation
