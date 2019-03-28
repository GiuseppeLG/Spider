# Spider

It's a robot centered on a specific topic, such as to follow and index all the interesting pages of this topic neglecting the rest. Developed in Python.


## Installation

You have to install simply a few of library with pip3, in particular the "h2" lib in v2.6.2 [ISSUE](https://github.com/python-hyper/hyper-h2/issues/1050#issuecomment-344324820)
```bash
pip install --upgrade h2>=2.4,<3.0,!=2.5.0
```

## Usage
To run, you must have a local db (or remote with free access from python, you can check it in your hosting provider). Then it's configured for one db table named "Siti", you can remane it of course.
```python
configDB = [w.replace('host=', '') for w in configDB]  # set hostname 
configDB = [w.replace('user=', '') for w in configDB]  # set username of db
configDB = [w.replace('database=', '') for w in configDB]  # set database name

# to add password you have to edit:
 mydb = mysql.connector.connect(
            host=host,
            user=user,
            database=database
            #  add passwd="" to insert password
        )

```

## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

Please make sure to update tests as appropriate.

## License
This software is free.
[GPL](http://www.gnu.org/licenses/gpl.html)

