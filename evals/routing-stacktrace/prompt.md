My script crashed with this. What's wrong?

```
Traceback (most recent call last):
  File "app.py", line 12, in <module>
    main()
  File "app.py", line 8, in main
    total = sum(p["amount"] for p in prices)
  File "app.py", line 8, in <genexpr>
    total = sum(p["amount"] for p in prices)
TypeError: unsupported operand type(s) for +: 'int' and 'str'
```
