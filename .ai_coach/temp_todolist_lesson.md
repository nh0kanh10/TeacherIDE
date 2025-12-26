# ASP.NET MVC TodoList - Ví dụ Thực Tế

## 🎯 Mục tiêu
Xây dựng Todo List App đơn giản để hiểu rõ MVC Pattern:
- Thêm task mới
- Xem danh sách task
- Đánh dấu hoàn thành
- Xóa task

---

## 📁 Cấu trúc Project

```
TodoListMVC/
├── Models/
│   └── Todo.cs              ← Dữ liệu & Logic
├── Controllers/
│   └── TodoController.cs    ← Điều khiển
├── Views/
│   └── Todo/
│       ├── Index.cshtml     ← Danh sách
│       └── Create.cshtml    ← Form thêm mới
└── Program.cs               ← Entry point
```

---

## 🧱 BƯỚC 1: Tạo MODEL (Dữ liệu)

**File: `Models/Todo.cs`**

```csharp
namespace TodoListMVC.Models
{
    public class Todo
    {
        // Properties (Thuộc tính)
        public int Id { get; set; }
        public string Title { get; set; }
        public bool IsCompleted { get; set; }
        public DateTime CreatedAt { get; set; }
        
        // Constructor
        public Todo()
        {
            CreatedAt = DateTime.Now;
            IsCompleted = false;
        }
        
        // Business Logic
        public void MarkAsCompleted()
        {
            IsCompleted = true;
        }
    }
}
```

### 💡 Giải thích Model:
- **Properties**: Các trường dữ liệu (Id, Title, IsCompleted...)
- **Constructor**: Khởi tạo giá trị mặc định
- **Methods**: Hàm nghiệp vụ (MarkAsCompleted)

**👉 Model = "Kho dữ liệu + Quy tắc xử lý"**

---

## 🎮 BƯỚC 2: Tạo CONTROLLER (Điều khiển)

**File: `Controllers/TodoController.cs`**

```csharp
using Microsoft.AspNetCore.Mvc;
using TodoListMVC.Models;

namespace TodoListMVC.Controllers
{
    public class TodoController : Controller
    {
        // Fake database (In-memory list)
        private static List<Todo> todos = new List<Todo>();
        
        // ACTION 1: Hiển thị danh sách
        public IActionResult Index()
        {
            // Lấy data từ "database"
            var allTodos = todos;
            
            // Truyền data cho View
            return View(allTodos);
        }
        
        // ACTION 2: Hiển thị form tạo mới
        [HttpGet]
        public IActionResult Create()
        {
            return View();
        }
        
        // ACTION 3: Xử lý form submit
        [HttpPost]
        public IActionResult Create(string title)
        {
            if (string.IsNullOrEmpty(title))
            {
                // Validation failed
                ModelState.AddModelError("", "Title không được trống!");
                return View();
            }
            
            // Tạo Todo mới
            var newTodo = new Todo
            {
                Id = todos.Count + 1,
                Title = title
            };
            
            // Lưu vào "database"
            todos.Add(newTodo);
            
            // Redirect về trang Index
            return RedirectToAction("Index");
        }
        
        // ACTION 4: Đánh dấu hoàn thành
        public IActionResult Complete(int id)
        {
            var todo = todos.FirstOrDefault(t => t.Id == id);
            if (todo != null)
            {
                todo.MarkAsCompleted();
            }
            
            return RedirectToAction("Index");
        }
        
        // ACTION 5: Xóa task
        public IActionResult Delete(int id)
        {
            var todo = todos.FirstOrDefault(t => t.Id == id);
            if (todo != null)
            {
                todos.Remove(todo);
            }
            
            return RedirectToAction("Index");
        }
    }
}
```

### 💡 Giải thích Controller:
- **Index()**: Lấy data → Gửi cho View
- **Create() [GET]**: Hiển thị form
- **Create() [POST]**: Nhận data → Validate → Lưu → Redirect
- **Complete()**: Tìm item → Cập nhật → Redirect
- **Delete()**: Tìm item → Xóa → Redirect

**👉 Controller = "Bộ điều phối requests"**

---

## 🎨 BƯỚC 3: Tạo VIEW (Giao diện)

### VIEW 1: Danh sách (`Views/Todo/Index.cshtml`)

```html
@model List<TodoListMVC.Models.Todo>

<!DOCTYPE html>
<html>
<head>
    <title>My Todo List</title>
    <style>
        body { font-family: Arial; margin: 40px; }
        .todo-item { 
            padding: 15px; 
            border: 1px solid #ddd; 
            margin: 10px 0; 
            border-radius: 5px;
        }
        .completed { 
            text-decoration: line-through; 
            color: #999; 
        }
        .btn { 
            padding: 5px 15px; 
            margin: 0 5px; 
            cursor: pointer; 
        }
        .btn-success { background: #28a745; color: white; }
        .btn-danger { background: #dc3545; color: white; }
    </style>
</head>
<body>
    <h1>📝 My Todo List</h1>
    
    <a href="@Url.Action(`Create`)" class="btn btn-primary">➕ Thêm Task Mới</a>
    
    <hr>
    
    @if (Model.Count == 0)
    {
        <p>Chưa có task nào. Hãy thêm mới!</p>
    }
    else
    {
        foreach (var todo in Model)
        {
            <div class="todo-item">
                <span class="@(todo.IsCompleted ? "completed" : "")">
                    @todo.Title
                </span>
                
                <span style="float: right;">
                    @if (!todo.IsCompleted)
                    {
                        <a href="@Url.Action("Complete", new { id = todo.Id })" 
                           class="btn btn-success">✓ Hoàn thành</a>
                    }
                    
                    <a href="@Url.Action("Delete", new { id = todo.Id })" 
                       class="btn btn-danger">🗑️ Xóa</a>
                </span>
            </div>
        }
    }
</body>
</html>
```

### VIEW 2: Form thêm mới (`Views/Todo/Create.cshtml`)

```html
<!DOCTYPE html>
<html>
<head>
    <title>Thêm Task Mới</title>
    <style>
        body { font-family: Arial; margin: 40px; }
        input[type="text"] { 
            width: 400px; 
            padding: 10px; 
            font-size: 16px; 
        }
        .btn { 
            padding: 10px 20px; 
            font-size: 16px; 
            cursor: pointer; 
        }
    </style>
</head>
<body>
    <h1>➕ Thêm Task Mới</h1>
    
    <form method="post" action="@Url.Action("Create")">
        <div>
            <label>Tên Task:</label><br>
            <input type="text" name="title" placeholder="Nhập tên task..." />
        </div>
        
        <br>
        
        <button type="submit" class="btn">💾 Lưu</button>
        <a href="@Url.Action("Index")">❌ Hủy</a>
    </form>
</body>
</html>
```

### 💡 Giải thích View:
- `@model List<Todo>`: Khai báo kiểu dữ liệu nhận từ Controller
- `@foreach`: Loop qua danh sách
- `@Url.Action("Create")`: Tạo link đến action
- Razor syntax: `@todo.Title` để hiển thị dữ liệu

**👉 View = "Template HTML + Data"**

---

## 🔄 FLOW HOÀN CHỈNH

### Kịch bản 1: User xem danh sách

```
1. User truy cập: /Todo/Index
2. TodoController.Index() được gọi
3. Controller lấy List<Todo> từ database
4. Truyền data cho View: return View(allTodos)
5. Index.cshtml nhận data, render HTML
6. Browser hiển thị danh sách
```

### Kịch bản 2: User thêm task mới

```
1. User click "Thêm Task"
2. TodoController.Create() [GET] → Hiển thị form
3. User điền tên task → Submit
4. TodoController.Create(title) [POST] được gọi
5. Controller validate → Tạo Todo → Lưu vào list
6. RedirectToAction("Index") → Quay lại trang danh sách
7. Danh sách hiển thị task mới
```

---

## ✅ CHECKLIST KIỂM TRA

- [ ] Model có Properties, Constructor, Methods?
- [ ] Controller có Actions: Index, Create (GET/POST)?
- [ ] View có `@model` declaration?
- [ ] View sử dụng `@Url.Action` cho links?
- [ ] Flow: User → Controller → Model → View → User?

---

## 🎯 BÀI TẬP

Hãy thử thêm tính năng:
1. **Edit Task**: Sửa tên task
2. **Filter**: Chỉ hiển thị task chưa hoàn thành
3. **Search**: Tìm task theo tên

---

## 📌 TÓM TẮT

| Thành phần | File | Nhiệm vụ |
|---|---|---|
| **Model** | `Todo.cs` | Định nghĩa dữ liệu (Id, Title, IsCompleted) |
| **Controller** | `TodoController.cs` | Xử lý requests (Index, Create, Delete...) |
| **View** | `Index.cshtml`, `Create.cshtml` | Hiển thị HTML cho user |

**MVC = Chia để trị = Code dễ maintain!**
