CREATE TABLE IF NOT EXISTS public.Department(
    Id INTEGER GENERATED ALWAYS AS  IDENTITY PRIMARY KEY,
    Code  VARCHAR(255),
    Title VARCHAR(255) ,
    Url  TEXT,
    ScrapedAt TIMESTAMPTZ
);
CREATE TABLE IF NOT EXISTS public.categories(
    Id INTEGER GENERATED ALWAYS AS  IDENTITY PRIMARY KEY,
    Code  VARCHAR(255),
    Category VARCHAR(255) ,
    SubCategory VARCHAR(255) ,
    Url  TEXT,
    DepartmentCode VARCHAR(255),
    ScrapedAt TIMESTAMPTZ
);
CREATE TABLE IF NOT EXISTS public.subsubcategories(
    Id INTEGER GENERATED ALWAYS AS  IDENTITY PRIMARY KEY,
    Code  VARCHAR(255),
    name VARCHAR(255) ,
    Url  TEXT,
    SubcategoriesCode VARCHAR(255),
    ScrapedAt TIMESTAMPTZ
);
CREATE TABLE IF NOT EXISTS public.subcategories(
    Id INTEGER GENERATED ALWAYS AS  IDENTITY PRIMARY KEY,
    Code  VARCHAR(255),
    name VARCHAR(255) ,
    url TEXT,
    CategoriesCode VARCHAR(255),
    ScrapedAt TIMESTAMPTZ
);
CREATE TABLE IF NOT EXISTS public.Product(
    Id INTEGER GENERATED ALWAYS AS  IDENTITY PRIMARY KEY,
    Code  VARCHAR(255),
    category_id VARCHAR(255) ,
    subcategory_id  VARCHAR(255) ,
    subsubcategory_id VARCHAR(255),
    image TEXT,
    name VARCHAR(255),
    reference TEXT,
    price TEXT,
    initial_price TEXT,
    saved_price TEXT,
    stock_status VARCHAR(255),
    reviews  VARCHAR(255),
    key_features TEXT,
    ScrapedAt TIMESTAMPTZ
);
CREATE TABLE IF NOT EXISTS public.filters(
    Id INTEGER GENERATED ALWAYS AS  IDENTITY PRIMARY KEY,
    Code  VARCHAR(255),
    category_code VARCHAR(255) ,
    subcategory_code VARCHAR(255) ,
    subsubcategory_code  VARCHAR(255),
    filter VARCHAR(255),
    options VARCHAR(255),
    ScrapedAt TIMESTAMPTZ
)