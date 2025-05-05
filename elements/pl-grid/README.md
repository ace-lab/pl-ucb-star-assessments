# PrairieLearn OER Element: Grid

This element was developed by Kiriratanak Vong, Runjeet Narula, and Anika Sikka. Please carefully test the element and understand its features and limitations before deploying it in a course. It is provided as-is and not officially maintained by PrairieLearn, so we can only provide limited support for any issues you encounter!

If you like this element, you can use it in your own PrairieLearn course by copying the contents of the `elements` folder into your own course repository. After syncing, the element can be used as illustrated by the example question that is also contained in this repository.

## `pl-grid` element

This element creates 3 grids and can be used for both instructional materials and questions. The number of columns is set to a fixed width of 12. The number of rows is not restricted to any set number and will continue increasing as more blocks are defined. 

The first grid contains all of the blocks that can be used to create the solution. These blocks are currently set to be duplicated. To delete the duplicates, drag them back from the second grid into the first grid.

The second grid should contain blocks that represent the student-made solution. Optionally, you can have part of the solution filled out by defining those blocks. These will not be factored into the grading.

The third grid contains blocks that represent the true solution set by instructors. This will be hidden from the students and is used for grading. 

The table supports partial grading based on the number of blocks that match the true solution, aside from the predefined blocks.

### Example

![Screenshot 2025-05-05 at 2.21.45 PM.png](PrairieLearn%20OER%20Element%20Grid%201e6f365af52380d386c4f7f64dbf48e1/Screenshot_2025-05-05_at_2.21.45_PM.png)

```html
<pl-grid color-column = "true">
    <pl-source> <!-- Define elements in source grid -->
        <pl-element x = "0", y = "0", h = "2">read y</pl-element>
        <pl-element x = "2", y = "0", color = "#ffffff">y+</pl-element>
        <pl-element x = "4", y = "0", color = "#ffffff">y-</pl-element>
        <pl-element x = "6", y = "0", color = "#ffffff">write y</pl-element>
    </pl-source>

    <pl-destination> <!-- Define how destination grid is prepopulated -->
        <pl-element x = "0", y = "0", color = "#d8bfd8">main</pl-element>
        <pl-element x = "0", y = "1", color = "#d8bfd8">init y</pl-element>
        <pl-element x = "0", y = "2", color = "#d8bfd8">#pragma omp parallel</pl-element>
        <pl-element x = "2", y = "2", color = "#f08080">thread 1</pl-element>
        <pl-element x = "4", y = "2", color = "#e0ffff">thread 2</pl-element>
    </pl-destination>
    
    <pl-answer-grid> <!-- Define solution grid (not shown to student) -->
        <pl-element x = "0", y = "0">main</pl-element>
        <pl-element x = "0", y = "1">init y</pl-element>
        <pl-element x = "0", y = "2">#pragma omp parallel</pl-element>
        <pl-element x = "2", y = "2">thread 1</pl-element>
        <pl-element x = "4", y = "2">thread 2</pl-element>
        <pl-element x = "2", y = "3", h = "2">read y</pl-element>
        <pl-element x = "2", y = "5">y+</pl-element>
        <pl-element x = "2", y = "6">write y</pl-element>
    </pl-answer-grid>
</pl-grid>
```

### Element (pl-grid) Attributes

| Attribute | Type | Description |
| --- | --- | --- |
| `color-column` | boolean (default: `false`) | If set to `true`, blocks dragged into the second grid will be colored the same color as the first non-white block in their column. This does not work when dragging between columns in the same grid.  |

### Block (pl-element) Attributes

| Attribute | Type | Description |
| --- | --- | --- |
| `x` | string (required) | The x-position of the block (0-indexed, i.e., the leftmost column is 0). Make sure to take width of blocks into account when determining the value. |
| `y` | string (required) | The y-position of the block (0-indexed, i.e., the topmost row is 0). Make sure to take the height of blocks into account when determining the value. |
| `w` | string (default: `"2"`) | The width of the block. |
| `h` | string (default: `"1"`) | The height of the block |
| `color` | string (default: `"#ffffff"`) | The color of the block. |