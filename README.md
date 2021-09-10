# ztrace

There must be lots of values and parameters you care about in the experiment, such as `num_epochs, learning_rate, train_loss, test_accuracy` in the deep learning experiment. You always need to write some code to record them which is boring and annoying.

**Now, `ztrace` allows you to trace them conveniently by only adding a single line of code!**

## Run

Clone me and:

- test: `cd example; python basic.py`.
- use in your own program (temporally)

  ```python
  import sys
  sys.path.insert('abs path of ztrace program directory')
  from ztrace import ztrace
  ```

  `ztrace` will be released in `pip` soon.

## Tips

- Use `repr(last_var) == repr(cur_var)` to judge whether the key variables have changed once a line of code is executed (inspired by [cool-RR/PySnooper](https://github.com/cool-RR/PySnooper)) . The performance will not be affected significantly when normally used. See Benchmark for more information.
- In a run, all records of key variables changed will be saved in `./ztrace_logs/${date}/${time}.json` via readable format:

  Example code:

  ```python
  @ztrace(['variable_a', 'variable_b'])
  def func_a(t):
      variable_a, variable_b = 0, 0
      for i in range(t):
          variable_a = i
          variable_b = i * 2

  @ztrace(['variable_a'])
  def func_b(t):
      variable_a = ''
      for i in range(t):
          variable_a += str(i)

  func_a(3)
  func_a(4)
  func_b(3)
  ```

  The exported record will be:

  ```json
  {
    "func_a()": [
      // run func_a() firstly
      {
        "data": {
          "variable_a": [0, 1, 2], // the value of variable_a has changed for three times in func_a()
          "variable_b": [0, 2, 4],
        },
        "time": "20210910151123" // when func_a() exits
      },
      // run func_a() again
      {
        "data": {
          "variable_a": [0, 1, 2, 3],
          "variable_b": [0, 2, 4, 6],
        },
        "time": "20210910151123"
      }
    ],
    "func_b()": [
      {
        "data": {
          "variable_a": ["", "0", "01", "012"]
        },
        "time": "20210910151123"
      }
    ]
  }
  ```

## Example

### Basic usage

1. Trace basic immutable data:

   ```python
   @ztrace(['t', 'res'])
   def trace_basic_immutable_data(t):
       res = 0
       for i in range(t):
           res += i
       res *= 2

       res = ''
       for i in range(t):
           res += str(i)
       res *= 2

   trace_basic_immutable_data(3)
   # tracing record:
   # {'t': 3, 'res': [0, 1, 3, 6, '', '0', '01', '012', '012012']}
   ```
2. Trace basic mutable data:

   ```python
   @ztrace(['arr', 'obj'])
   def trace_basic_mutable_data(t):
       arr = []
       obj = {}
       for i in range(t):
           arr += [i]
           obj[str(i)] = i

   trace_basic_mutable_data(3)
   # tracing record:
   # {'arr': [[], [0], [0, 1], [0, 1, 2]], 'obj': [{}, {'0': 0}, {'0': 0, '1': 1}, {'0': 0, '1': 1, '2': 2}]}
   ```
3. Trace attributes or elements of `array / dict / object`:

   ```python
   @ztrace(['arr[1]', 'obj["a"]["b"]', 'cls.a'])
   def trace_attr(t):
       arr = [None for _ in range(t)]
       obj = {'a': {'b': None}}
       class Cls:
           a = None
       cls = Cls()

       for i in range(t):
           arr[1] = i
           obj['a']['b'] = i
           cls.a = i

   trace_attr(3)
   # tracing record:   
   # {'arr[1]': [None, 0, 1, 2], 'obj["a"]["b"]': [None, 0, 1, 2], 'cls.a': [None, 0, 1, 2]}
   ```
4. Trace special array (`ndarray / torch.Tensor`):

   ```python
   @ztrace(['arr', 'arr[1]', 'tensor', 'tensor[1]'])
   def trace_special_array(t):
       arr = np.zeros((t, ))
       tensor = torch.zeros((t, ))

       for i in range(t):
           arr[i] = i
           tensor[i] = i

       tensor = torch.cat([
           tensor,
           torch.from_numpy(arr).float()
       ])

   trace_special_array(3)
   """
   tracing record:
   {
   	'arr': [array([0., 0., 0.]), array([0., 1., 0.]), array([0., 1., 2.])], 
   	'arr[1]': [0.0, 1.0], 
   	'tensor': [tensor([0., 0., 0.]), tensor([0., 1., 0.]), tensor([0., 1., 2.]), tensor([0., 1., 2., 0., 1., 2.])], 
   	'tensor[1]': [tensor(0.), tensor(1.)]
   }
   """
   ```

### Advanced usage

1. Ignore some value changes:

   Add line comment `# ztrace: ignore` after code to ignore value changes in this line of code.

   ```python
   @ztrace(['t', 'res'])
   def trace_with_ignoring(t):
       res = 0
       for i in range(t):
           res += i # ztrace: ignore
       res *= 2

       res = '' # ztrace: ignore
       for i in range(t):
           res += str(i)
       res *= 2

   trace_with_ignoring(3)
   # tracing record:
   # {'t': 3, 'res': [0, 6, '0', '01', '012', '012012']}
   ```

   Typical scene: tracing `training_loss` in model training:

   ```python
   # pseudo-code

   @ztrace(['training_loss'])
   def train():
       for epoch_index in range(num_epochs):
           training_loss = 0. # ztrace: ignore
           for batch_index, (data, target) in enumerate(train_lodaer):
               training_loss += loss.item() # ztrace: ignore
           training_loss /= len(train_loader)
   ```

## TODO

- custom hooks
- export more necessary information
- benchmark
- ...

## Benchmark

TODO
