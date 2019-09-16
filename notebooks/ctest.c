#include<stdio.h>
#include<string.h>

struct Complex {
	double x;
	double y;
};


struct Complex add(struct Complex c, struct Complex d) {
	struct Complex tmp;
	printf("%f %f\n", c.x+d.x, c.y+d.y);
	tmp.x = c.x + d.x;
	tmp.y = c.y + d.y;
	return tmp;
}

void swap(struct Complex *c, struct Complex *d) {
	struct Complex tmp;
	tmp = *c;
	*c = *d;
	*d = tmp;
}

void mult(double a[][100], double b[][100], double c[][100], int m, int r, int n) { /* good old matrix multiplication */
	int i, j, k;
	for (int i = 0; i < m; i++) 
		for (int j = 0; j < n; j++)   {
			c[i][j] = 0;
			for (k = 0; k < r; k++)
				c[i][j] += a[i][k] * b[k][j];
		}
}

#define small(c) ( (c >= 97) && ( c <= 97+26))
#define capit(c) ( (c >= 65) && ( c <= 65+26))
#define letter(c) (small(c) || capit(c))
#define toup(c) (c - 32 )
#define tolow(c) (c + 32)

void titlecase(char *str) {	/* make  a string title case. All word boundaries start with capital, others small */
	int i;
	int out = 1;
	for (i = 0; str[i]; i++) {
		if (letter(str[i])) {
			if (out && small(str[i])) {
				out = 0;
				str[i] = toup(str[i]);
			} else if (! out && capit(str[i])) {
				str[i] = tolow(str[i]);
			}
		} else  if (! out ) 
			out = 1;
	}
}

int tokenize(char sep, char *str, char t[][20]) { /* tokenize string with given seperator, return number of items */
	char sepstr[] = {sep, 0};
	char *tok;
	int i;

	tok = strtok(str, sepstr);
	for (i = 0; tok != NULL; i++) {
		strncpy(t[i], tok, 100);
		tok = strtok(NULL, sepstr);
	}
	return i;
}

double sum(double f[], int n)
{
	int i;
	double s = 0;

	for (i = 0; i < n; i++) {
		s += f[i];
	}

	return s;
}
