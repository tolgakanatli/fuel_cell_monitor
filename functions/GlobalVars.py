from typing import Literal, Callable, Any
import tkinter as tk
from dataclasses import dataclass

class GlobalVars:
    """
    A singleton class to manage global variables in a structured way.

    This class provides a centralized repository for global variables, 
    allowing you to access and modify them using dot notation (g.var_name). 
    It also supports type enforcement, custom getter/setter functions, 
    and integration with tkinter widgets for easy GUI development.

    Attributes:
        all_gvars (dict[str, 'GlobalVar']): A dictionary storing all registered global variables.
            The keys are variable names (str), and the values are GlobalVar instances.
        _instance (GlobalVars): The private class instance, ensuring the singleton pattern.

    Example:
        >>> gv = GlobalVars()
        >>> GlobalVar("my_var", 10, int)  # Create a global integer variable
        >>> print(gv.my_var)  # Access using dot notation
        10
        >>> gv.my_var = 20  # Modify the variable
        >>> print(gv.my_var)
        20
    """
    all_gvars: dict[str, 'GlobalVar'] = {}
    _instance = None

    def __new__(cls):
        """
        Implements the singleton pattern, ensuring only one instance of GlobalVars exists.

        Returns:
            GlobalVars: The single instance of the GlobalVars class.
        """
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __getattr__(self, name: str) -> Any:
        """
        Intercepts attribute access to return the value of a registered global variable.

        If the attribute is a registered global variable, it returns its value.
        Otherwise, it behaves like regular attribute access.

        Args:
            name (str): The name of the attribute.

        Returns:
            Any: The value of the attribute.

        Raises:
            KeyError: If the requested attribute is not a registered global variable.
        """
        if name in self.all_gvars:
            return self.all_gvars[name].var
        else:
            raise KeyError(f"No such global variable: {name}")

    def __setattr__(self, name: str, value: Any):
        """
        Intercepts attribute assignment to update the value of a registered global variable.

        If the attribute is a registered global variable, it updates its value.
        Otherwise, it behaves like regular attribute assignment.

        Args:
            name (str): The name of the attribute.
            value (Any): The new value to set.

        Raises:
            KeyError: If attempting to set a global var that doesn't exist.
        """
        if name in self.all_gvars:
            self.all_gvars[name].var = value
        else:
            if not hasattr(self, name):
                raise KeyError(f"No such global variable: {name}. Use GlobalVar to create one.")
            else:
                super().__setattr__(name, value)

    def __delattr__(self, name: str):
        """
        Deletes a registered global variable.

        Args:
            name (str): The name of the global variable to delete.

        Raises:
            KeyError: If attempting to delete a global variable that doesn't exist.
        """
        if name in self.all_gvars:
            del self.all_gvars[name]
            instance_key = name + "_instance"
            if instance_key in self.__dict__:
                del self.__dict__[instance_key]
        else:
            raise KeyError(f"No such global variable: {name}")

    def register(self, gvar: 'GlobalVar') -> None:
        """
        Registers a GlobalVar instance with the GlobalVars singleton.

        Args:
            gvar (GlobalVar): The GlobalVar instance to register.

        Raises:
            ValueError: If a variable with the same name is already registered.
            AttributeError: If the variable name conflicts with an existing class attribute.
        """
        if gvar.name in self.all_gvars:
            raise ValueError(f"Global variable {gvar.name} already registered.")
        if gvar.name in self.__dict__:
            raise AttributeError(f"The name '{gvar.name}' conflicts with an existing class attribute.")

        self.all_gvars[gvar.name] = gvar
        super().__setattr__(gvar.name + "_instance", gvar)

    def __repr__(self) -> str:
        return "GlobalVars()"

    def __str__(self) -> str:
        return str(self.all_gvars)


@dataclass
class GlobalVar:
    """
    Represents a single global variable with optional type enforcement, custom getter/setter functions, and tkinter widget association.

    Attributes:
        name (str): The name of the global variable.
        _var (Any, optional): The actual value stored in the variable. Defaults to None.
        data_type (Callable[[Any], Any], optional): A callable (e.g., int, str) to enforce the variable's type. Defaults to None.
        getterfunc (Callable[[Any], Any], optional): A function to retrieve the value, allowing custom logic. Defaults to None. 
        setterfunc (Callable[[Any], Any], optional): A function to set the value, enabling actions upon modification. Defaults to None.
        widget (tk.Widget, optional): A tkinter widget associated with the variable (e.g., an Entry for text input). Defaults to None.
        widget_type (Literal['entry', 'text', 'checkbutton', 'scale', 'combobox'], optional): The type of tkinter widget. Defaults to None.
    """

    name: str
    _var: Any | None = None
    data_type: Callable[[Any], Any] | None = None
    getterfunc: Callable[[Any], Any] | None = None
    setterfunc: Callable[[Any], Any] | None = None
    widget: tk.Widget | None = None
    widget_type: Literal['entry', 'text', 'checkbutton', 'scale', 'combobox'] | None = None

    def __post_init__(self):
        """Registers the GlobalVar instance with the GlobalVars singleton after initialization."""
        gv = GlobalVars()
        gv.register(self)

    @property
    def var(self) -> Any:
        """
        Provides controlled access to the variable's value.

        Retrieves the value from the getter function, associated widget, or internal storage.
        Applies type casting if specified.

        Returns:
            Any: The value of the global variable.
        """
        interimval = self._var
        if self.widget and self.widget_type:
            interimval = self.get_widget_value()
            
        if self.data_type:
            interimval = self.data_type(interimval)
            
        if self.getterfunc:
            interimval = self.getterfunc(interimval)

        if self.data_type:
            interimval = self.data_type(interimval)

        self._var = interimval
        return self._var

    def __repr__(self) -> str:
        typename = self.data_type.__name__ if self.data_type else "Any"
        return f"GlobalVar({self.name}, {self._var}, data_type={typename})"

    def __str__(self) -> str:
        return str(self._var)

    @var.setter
    def var(self, value: Any):
        """
        Sets the value of the global variable.

        Updates the internal storage, executes the setter function if provided,
        and updates the associated tkinter widget if applicable.

        Args:
            value (Any): The new value to set.
        """
        self._var = value
        if self.setterfunc:
            self._var = self.setterfunc(value)

        self.set_widget_value(self._var)
        

    def get_widget_value(self) -> Any:
        """
        Retrieves the value from the associated tkinter widget.

        Returns:
            Any: The value retrieved from the widget, cast to the specified data type if applicable.
                 Returns None if no widget is associated or an unsupported widget type is used.

        Raises:
            ValueError: If an unsupported widget type is specified.
        """
        val = None
        if self.widget_type == 'text':
            val = self.widget.get("1.0", tk.END).strip()
        elif self.widget_type in ['entry', 'scale', 'combobox', 'checkbutton']:
            val = self.widget.get()
        else:
            raise ValueError(f"Unsupported widget type: {self.widget_type}")

        if self.data_type:
            return self.data_type(val)
        else:
            return val

    def set_widget_value(self, value) -> None:
        """Sets the value of the associated widget based on its type."""
        if self.widget_type == 'entry':
            self.widget.delete(0, tk.END)
            self.widget.insert(0, value)
        elif self.widget_type == 'text':
            self.widget.delete("1.0", tk.END)
            self.widget.insert(tk.END, value)
        elif self.widget_type in ['checkbutton', 'scale', 'combobox']:
            self.widget.set(value)


def run_console_test():
    # 1. Basic Usage:
    print("## Basic Usage:")
    GlobalVar("my_int", 10, int)
    GlobalVar("my_str", "Hello", str)
    GlobalVar("my_float", 3.14, float)

    gv = GlobalVars()
    print(f"my_int: {gv.my_int}")
    print(f"my_str: {gv.my_str}")
    print(f"my_float: {gv.my_float}")

    # 2. Type Enforcement:
    print("\n## Type Enforcement:")
    try:
        gv.my_int = "invalid"  # Attempt to assign a string to an integer variable
    except ValueError as e:
        print(f"Error: {e}")

    # 3. Custom Getter/Setter:
    print("\n## Custom Getter/Setter:")
    def custom_getter(value):
        return f"Value: {value} (custom)!"

    def custom_setter(value):
        print(f"Setting custom variable to: {value}")
        return value.upper()

    GlobalVar("custom_var", "initial", getterfunc=custom_getter, setterfunc=custom_setter)
    print(f"custom_var: {gv.custom_var}")
    gv.custom_var = "new value"
    print(f"custom_var: {gv.custom_var}")

    # 4. Mutable Data Types:
    print("\n## Mutable Data Types:")
    GlobalVar("my_list", [1, 2, 3], list)
    print(f"my_list: {gv.my_list}")
    gv.my_list.append(4)
    print(f"my_list: {gv.my_list}")

    GlobalVar("my_dict", {"key1": "value1", "key2": "value2"}, dict)
    print(f"my_dict: {gv.my_dict}")
    print(f"key3 in my_dict: {gv.my_dict['key3']}")
    gv.my_dict["key3"] = "value3"
    print(f"my_dict: {gv.my_dict}")

    # 5. Deletion:
    print("\n## Deletion:")
    GlobalVar("to_delete", 5, int)
    print(f"to_delete: {gv.to_delete}")
    del gv.to_delete
    try:
        print(f"to_delete: {gv.to_delete}")  # This should raise an error
    except KeyError as e:
        print(f"Error: {e}")


def run_gui_test():
    root = tk.Tk()
    root.title("GlobalVar Demo - All Widgets")

    # --- Layout using Grid ---
    root.columnconfigure(0, weight=1)
    root.columnconfigure(1, weight=1)

    # 1. Entry Widget
    entry_label = tk.Label(root, text="Enter Text:")
    entry_label.grid(row=0, column=0, sticky="w")
    entry_widget = tk.Entry(root)
    entry_widget.grid(row=0, column=1, sticky="ew")
    GlobalVar("entry_var", widget=entry_widget, widget_type='entry', data_type=str)
    entry_widget.insert(0, "Initial Text")

    # 2. Text Widget
    text_label = tk.Label(root, text="Enter Multiline Text:")
    text_label.grid(row=1, column=0, sticky="w")
    text_widget = tk.Text(root, height=3)
    text_widget.grid(row=1, column=1, sticky="ew")
    GlobalVar("text_var", widget=text_widget, widget_type='text', data_type=str)
    text_widget.insert(tk.END, "Initial Multiline Text")

    # 3. Checkbutton Widget
    check_label = tk.Label(root, text="Check me:")
    check_label.grid(row=2, column=0, sticky="w")
    check_var = tk.BooleanVar(value=False)
    check_widget = tk.Checkbutton(root, text="Check me!", variable=check_var)
    check_widget.grid(row=2, column=1, sticky="w")
    GlobalVar("check_var", widget=check_var, widget_type='checkbutton', data_type=bool)

    # 4. Scale Widget
    scale_label = tk.Label(root, text="Select a value:")
    scale_label.grid(row=3, column=0, sticky="w")
    scale_widget = tk.Scale(root, from_=0, to=100, orient=tk.HORIZONTAL)
    scale_widget.grid(row=3, column=1, sticky="ew")
    GlobalVar("scale_var", widget=scale_widget, widget_type='scale', data_type=int)

    from tkinter import ttk
    # 5. Combobox Widget
    combobox_label = tk.Label(root, text="Choose an option:")
    combobox_label.grid(row=4, column=0, sticky="w")
    combobox_widget = ttk.Combobox(root, values=["Option 1", "Option 2", "Option 3"])
    combobox_widget.grid(row=4, column=1, sticky="ew")
    GlobalVar("combobox_var", widget=combobox_widget, widget_type='combobox', data_type=str)
    combobox_widget.current(0)  # Set initial selection

    # Output Area
    output_label = tk.Label(root, text="")
    output_label.grid(row=5, column=0, columnspan=2, sticky="ew")

    def update_output():
        """Gets values from all widgets and displays them in the output label."""
        gv = GlobalVars()
        output_text = (
            f"Entry: {gv.entry_var}\n"
            f"Text: {gv.text_var}\n"
            f"Check: {gv.check_var}\n"
            f"Scale: {gv.scale_var}\n"
            f"Combobox: {gv.combobox_var}"
        )
        output_label.config(text=output_text)

    # Create a button to trigger the output update
    update_button = tk.Button(root, text="Update Output", command=update_output)
    update_button.grid(row=6, column=0, columnspan=2, sticky="ew")

    def reset_widgets():
        """Resets all widgets to their initial values."""
        gv = GlobalVars()
        gv.entry_var = "Initial Text"
        gv.text_var = "Initial Multiline Text"
        gv.check_var = False
        gv.scale_var = 0
        gv.combobox_var = "Option 1"
        update_output()

    # Create a button to reset widgets
    reset_button = tk.Button(root, text="Reset Widgets", command=reset_widgets)
    reset_button.grid(row=7, column=0, columnspan=2, sticky="ew")

    root.mainloop()




if __name__ == "__main__":
    run_console_test()
    run_gui_test()
