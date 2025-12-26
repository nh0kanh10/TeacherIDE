# MVC Pattern - Kiến trúc "Chia để trị"

## MVC là gì?

**MVC** = **M**odel - **V**iew - **C**ontroller

Pattern để tổ chức code, chia ứng dụng thành 3 phần rõ ràng.

## Ví dụ Thực Tế: Quán Cafe

- **VIEW** = Menu + Phục vụ (cái user nhìn thấy)
- **CONTROLLER** = Nhân viên phục vụ (nhận yêu cầu, điều phối)
- **MODEL** = Bếp + Kho nguyên liệu (dữ liệu & xử lý)

## Code ASP.NET MVC

### Model (C# Class)
```csharp
public class Product
{
    public int Id { get; set; }
    public string Name { get; set; }
    public decimal Price { get; set; }
    public int Stock { get; set; }
    
    public bool IsAvailable() 
    {
        return Stock > 0;
    }
}
```

### Controller
```csharp
public class ProductController : Controller
{
    public IActionResult Index()
    {
        var products = GetProductsFromDatabase();
        return View(products);
    }
}
```

### View (Razor)
```html
@model List<Product>

<h1>Danh sách sản phẩm</h1>
<table>
    @foreach(var product in Model)
    {
        <tr>
            <td>@product.Name</td>
            <td>@product.Price VNĐ</td>
        </tr>
    }
</table>
```

## Tại sao dùng MVC?

- **Tách biệt concerns**: Dễ maintain
- **Dễ test**: Test từng phần riêng
- **Làm việc nhóm**: Người làm UI không ảnh hưởng logic

## Flow chuẩn

```
User click → Controller → Model (xử lý) → View (hiển thị) → User thấy
```

## Tóm tắt

| Thành phần | Nhiệm vụ | Ví dụ |
|---|---|---|
| Model | Dữ liệu + Logic | Class Product, tính giá |
| View | Giao diện HTML | Trang web |
| Controller | Điều khiển | Nhận request, gọi Model |
