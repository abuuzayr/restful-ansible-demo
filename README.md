# restful-ansible-demo

This is a simple `pyramid` app which illustrates how ansible can be
called from a trigger upon a rest endpoint.

## Dependencies

*Note: minor versions may not be that important. Listed are the
targeted environment specs*

**Python version: `3.6.0`**

Pip dependencies include the following:

+ `ansible==2.2.2.0`
+ `pyramid==1.8.3`

## Run the demo

Run `run.py` on python in the root project directory to run the demo.

Access to any routes defined in `app/__init__.py` to trigger the
endpoint. See the file itself for information.

## How to use the `.app.ansible.playbook.Playbook` class?

*Todo: document this inline with pydoc inside the class instead*

```python
pb = Playbook(
  playbooks=[
    # playbook file names
  ],
  options={
    # ansible options
  },
)

pb.play()
# playbooks will be played in order of the array.
```
