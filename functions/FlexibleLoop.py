import time
import inspect

class FlexibleWhile:
    """
    A flexible, customizable loop class that provides more control over loop behavior than the standard Python `while` loop.

    Attributes:
        before_func (callable, optional): A function to be executed before each iteration of the loop. This function can modify variables or perform actions that affect the loop's behavior. Defaults to None.
        cond_func (callable, optional): A function that determines the loop's condition. If this function returns True, the loop continues; if it returns False, the loop stops. Defaults to None.
        start_vals (tuple, optional): A tuple containing the initial values for variables used within the loop. Defaults to (None,).
        timeout (float, optional): A maximum time limit for the loop. If the loop runs for longer than this time, it will stop. Defaults to None.
        max_iterations (int, optional): A maximum number of iterations for the loop. If the loop runs for more iterations than this, it will stop. Defaults to None.
        on_timeout (callable, optional): A function to be called if the loop times out. Defaults to None.
        on_max_iterations (callable, optional): A function to be called if the loop reaches the maximum number of iterations. Defaults to None.
        values (tuple): A tuple that holds the current values of the loop's variables.
        start_time (float): Stores the time when the loop starts.
        iterations (int): Keeps track of the number of iterations the loop has completed.
    """
    def __init__(self, 
                 before_func=None, 
                 cond_func=None,
                 start_vals: tuple=(None,),
                 timeout=None, max_iterations=None,
                 on_timeout=None, 
                 on_max_iterations=None):
        
        """
        Initializes a FlexibleWhile object.

        Args:
            before_func (callable, optional): Function to execute before each iteration.
            cond_func (callable, optional): Function to determine loop condition. Setting to None is equivalent to "while True:". Defaults to None.
            start_vals (tuple, optional): Initial values for loop variables. Defaults to (None,). If your before_func uses values from previous loop, you must set these.
            timeout (float, optional): Maximum loop time in seconds.
            max_iterations (int, optional): Maximum loop iterations.
            on_timeout (callable, optional): Function to call on timeout.
            on_max_iterations (callable, optional): Function to call on max iterations.
        """
        
        self.before_func = before_func
        self.cond_func = cond_func
        self.timeout = timeout
        self.max_iterations = max_iterations
        self.on_timeout = on_timeout
        self.on_max_iterations = on_max_iterations
        self.values = start_vals
        self.start_time = None
        self.iterations = 0

    def __iter__(self):
        """
        Makes the FlexibleWhile object iterable, allowing it to be used in a for loop.

        Returns:
            self: The FlexibleWhile object itself.
        """
        self.start_time = time.time()
        self.iterations = 0
        return self

    def __next__(self):
        """
        Executes the next iteration of the loop.

        Returns:
            tuple: The current values of the loop's variables.

        Raises:
            StopIteration: If the loop condition is not met, the timeout is reached, or the maximum number of iterations is reached.
        """
        self.time_elapsed = time.time() - self.start_time
        if self.timeout and self.time_elapsed > self.timeout:
            if self.on_timeout:
                self._call_func(self.on_timeout)
            raise StopIteration("Timeout reached")

        if self.max_iterations and self.iterations >= self.max_iterations:
            if self.on_max_iterations:
                self._call_func(self.on_max_iterations)
            raise StopIteration("Max iterations reached")

        # Update values before checking the condition
        result = self._call_func(self.before_func)
        if result is not None:
            # Ensure values is a tuple
            if not isinstance(result, tuple):
                self.values = (result,)
            else:
                self.values = result

        # Check the condition function
        if self.cond_func and not self._call_func(self.cond_func):
            raise StopIteration("Condition not met")

        self.iterations += 1

        # Return values ensuring it's not a tuple if there's only one item
        if len(self.values) == 1:
            return self.values[0]
        else:
            return self.values

    def _call_func(self, func):
        """
        Calls a function with the appropriate arguments.

        Args:
            func (callable): The function to call.

        Returns:
            Any: The result of the function call.
        """
        if func is None:
            return
        if callable(func):
            # Use inspect to get function signature
            sig = inspect.signature(func)
            params = sig.parameters
            num_params = len(params)
            
            if num_params == 0:
                return func()
            elif num_params == 1:
                result = func(self.values[0])
                return result
            else:
                return func(*self.values)
        return


if __name__ == "__main__":
    print("Module loaded")
