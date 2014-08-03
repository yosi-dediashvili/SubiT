# SubiT's development

Some guidelines for the development

## Naming

We'll follow [python's guide]( http://legacy.python.org/dev/peps/pep-0008 ):

1. Module/File names: All lowercase, no underscore between words

```python 
modulename modulefile.py
```

2. Class names: CapWords
```python
ClassName
```
3. "Public" Function/Method/Variable names: All lowercase, underscore between words
```python
foo()
foo_two()
foo_var
```
4. "Private" Function/Method/Variable names: Same as 3, with leading underscore
```python
_foo()
_foo_two()
_foo_var
```

## Tests

We'll use two built-in mechanism of python for tests in SubiT. 

1. [doctest](https://docs.python.org/2/library/doctest.html) - for testing 
single functions regarding their api. These tests will cover simple tasks, like
verifying that exceptions are raised, and the right output is returned etc.
2. [unittest](https://docs.python.org/2/library/unittest.html) - for testing 
module flow and more complex function/module behavior.

### Structure

Each file in the **src** that has test written for it, should have its corresponding
file in the **tests** directory. The directory structure should be identical to the
src directory. The tests file names should start with `test_` and followed by
the original file name.

For example, the file `title.py`, will have a test file named `test_title.py`.

If a some file in the **src** has only doctests, it should have a test file also 
in the **tests** directory, and the tests will take care of the doctest execution.