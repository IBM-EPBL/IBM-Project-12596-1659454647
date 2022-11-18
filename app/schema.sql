-- create users table @dhivyaa

CREATE TABLE users (
  username character(30) NOT NULL, 
  password character(30) NOT NULL,
  email character(30) NOT NULL
);


CREATE TABLE wallet (
  id BIGSERIAL PRIMARY KEY,
  user_email CHARACTER(30) NOT NULL,
  balance FLOAT DEFAULT 0 NOT NULL,
  wallet_limit FLOAT DEFAULT 1000 NOT NULL,
  FOREIGN KEY (user_email) REFERENCES users(email)
);

CREATE TABLE expenses (
  user_email CHARACTER(30) NOT NULL,
  title character(50) NOT NULL,
  amount float NOT NULL,
  description character(100) NOT NULL,
  dateTime timestamp NOT NULL,
  credit BOOLEAN NOT NULL
);