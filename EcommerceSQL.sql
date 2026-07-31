-- ############################################################
-- E-Commerce Database System
-- DBMS: MySQL
-- ############################################################

DROP DATABASE IF EXISTS ecommerce;
CREATE DATABASE ecommerce;
USE ecommerce;

-- ############################################################
-- SCHEMA CREATION
-- ############################################################

CREATE TABLE Staff (
    StaffId     INT AUTO_INCREMENT PRIMARY KEY,
    FirstName   VARCHAR(50)  NOT NULL,
    LastName    VARCHAR(50)  NOT NULL,
    Email       VARCHAR(100) NOT NULL UNIQUE,
    Role        VARCHAR(50),
    DateHired   DATE
);

CREATE TABLE Customer (
    CustomerId  INT AUTO_INCREMENT PRIMARY KEY,
    FirstName   VARCHAR(50)  NOT NULL,
    LastName    VARCHAR(50)  NOT NULL,
    Email       VARCHAR(100) NOT NULL UNIQUE,
    Phone       VARCHAR(20),
    Address     VARCHAR(200)
);

CREATE TABLE Product (
    ProductId       INT AUTO_INCREMENT PRIMARY KEY,
    Name            VARCHAR(100) NOT NULL,
    Description     VARCHAR(500),
    Category        VARCHAR(50),
    Price           DECIMAL(10,2) NOT NULL,
    Stock           INT NOT NULL DEFAULT 0,
    ManagedBy       INT NOT NULL,
    CONSTRAINT CheckProductPrice CHECK (Price >= 0),
    CONSTRAINT CheckProductStock CHECK (Stock >= 0),
    CONSTRAINT fkProductStaff
        FOREIGN KEY (ManagedBy) REFERENCES Staff(StaffId)
);

CREATE TABLE CreditCard (
    CardId          INT AUTO_INCREMENT PRIMARY KEY,
    CustomerId      INT NOT NULL,
    card_number     VARCHAR(20)  NOT NULL,
    cardholder_name VARCHAR(100) NOT NULL,
    expiration_date DATE NOT NULL,
    billing_zip     VARCHAR(10),
    CONSTRAINT fkCardCustomer
        FOREIGN KEY (CustomerId) REFERENCES Customer(CustomerId)
);

CREATE TABLE Purchase (
    PurchaseId   INT AUTO_INCREMENT PRIMARY KEY,
    CustomerId   INT NOT NULL,
    ProductId    INT NOT NULL,
    CardId       INT NOT NULL,
    Quantity     INT NOT NULL,
    TotalPrice   DECIMAL(10,2) NOT NULL,
    DatePurchased DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT CheckPurchaseQuantity CHECK (Quantity > 0),
    CONSTRAINT fkPurchaseCustomer
        FOREIGN KEY (CustomerId) REFERENCES Customer(CustomerId),
    CONSTRAINT fkPurchaseProduct
        FOREIGN KEY (ProductId) REFERENCES Product(ProductId),
    CONSTRAINT fkPurchaseCard
        FOREIGN KEY (CardId) REFERENCES CreditCard(CardId)
);

-- ############################################################
-- SAMPLE DATA
-- ############################################################

-- Staff (3 rows)
INSERT INTO Staff (FirstName, LastName, Email, Role, DateHired) VALUES
('Jaques',      'Webster',  'jaques.webster@rapcenter.com',     'Manager',      '2016-03-30'),
('Jordan',      'Carter',   'jordan.carter@rapcenter.com',      'Inventory',    '2023-08-24'),
('Nayvadius',   'Wilburn',  'nayvadius.wilburn@rapcenter.com',  'Sales',        '2021-09-12');

-- Customer (5 rows)
INSERT INTO Customer (FirstName, LastName, Email, Phone, Address) VALUES
('Aubrey',  'Graham',   'aubrey.graham@gmail.com',      '101-010-1010', '5378 Drizzy Ln, New York City, NY'),
('Ken',     'Lamar',    'kendrick.duckworth@gmail.com', '323-232-3232', '3568 Kdot Ave, Los Angeles, CA'),
('Bill',    'Capri',    'bill.capri@gmail.com',         '545-454-5454', '3796 Kodak Rd, Miami, FL'),
('Tyler',   'Okonma',   'tyler.okonma@gmail.com',       '767-676-7676', '3579 Creator Blvd, Los Angeles, CA'),
('Symere',  'Woods',    'symere.woods@gmail.com',       '989-898-9898', '2345 Vert St, Philadelphia, PA');

-- Product (8 rows)
INSERT INTO Product (Name, Description, Category, Price, Stock, ManagedBy) VALUES
('Microphone',      'Best microphone for recording new hits',       'Electronics', 150.99,      50,  2),
('Keyboard',        'Electric keyboard with over 400 sounds',       'Electronics', 350.99,      50,  2),
('Notebook',        '100 pages w/ thick lines',                     'Home Office', 2.99,        100, 2),
('Pen',             'Black, ballpoint, and full of ink',            'Home Office', 0.99,        200, 2),
('Sound Panels',    'Best in the business for sound absorbtion',    'Accessories', 20.99,       200, 3),
('Headphones',      'Over-ear headphones with noise cancelling',    'Electronics', 200.99,      25,  3),
('Camera',          'Long battery life for extended use',           'Electronics', 550.99,      25,  3),
('Dinner w/ Jay-Z', 'Full 5 course meal with the legend himself',   'Experiences', 500000.00,   1,   1);

-- CreditCard (7 rows, some customers have multiple cards)
INSERT INTO CreditCard (CustomerId, card_number, cardholder_name, expiration_date, billing_zip) VALUES
(1, '1010101010101010', 'Aubrey Graham',    '2029-06-30', '10101'),
(1, '1100110011001100', 'Aubrey Graham',    '2028-08-31', '10101'),
(2, '3232323232323232', 'Ken Lamar',        '2030-11-30', '32323'),
(3, '5454545454545454', 'Bill Capri',       '2026-09-30', '54545'),
(4, '7676767676767676', 'Tyler Okonma',     '2028-02-28', '76767'),
(4, '7766776677667766', 'Tyler Okonma',     '2026-10-31', '76767'),
(5, '9898989898989898', 'Symere Woods',     '2029-03-31', '98989');

-- Purchase (10 rows)
-- TotalPrice = product price * quantity
INSERT INTO Purchase (CustomerId, ProductId, CardId, Quantity, TotalPrice, DatePurchased) VALUES
(1, 1, 1, 1,    150.99, '2026-07-03 10:15:00'),  -- Aubrey buys a microphone
(1, 2, 2, 1,    350.98, '2026-07-03 10:20:00'),  -- Aubrey buys a keyboard
(2, 2, 3, 1,    350.99, '2026-07-06 14:30:00'),  -- Ken buys a keyboard
(2, 3, 3, 2,    5.98,   '2026-07-06 14:35:00'),  -- Ken buys two notebooks
(3, 4, 4, 4,    3.96,   '2026-07-10 09:05:00'),  -- Bill buys four pens
(3, 5, 4, 9,    188.91, '2026-07-10 09:10:00'),  -- Bill buys nine sound panels
(4, 5, 5, 6,    125.94, '2026-07-15 11:20:00'),  -- Tyler buys six sound panels
(4, 6, 6, 1,    200.99, '2026-07-15 11:25:00'),  -- Tyler buys headphones
(5, 7, 7, 1,    550.98, '2026-07-18 13:55:00'),  -- Symere buys a camera
(5, 8, 7, 1, 500000.00, '2026-07-18 14:00:00');  -- Symere buys dinner w/ Jay-Z
