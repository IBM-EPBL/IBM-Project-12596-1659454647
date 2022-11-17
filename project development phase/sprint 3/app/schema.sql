-- create users table @dhivyaa

CREATE TABLE wallet (
  id BIGSERIAL PRIMARY KEY,
  username VARCHAR(30) NOT NULL,
  balance FLOAT DEFAULT 0 NOT NULL,
  wallet_limit FLOAT DEFAULT 1000 NOT NULL,
  FOREIGN KEY (username) REFERENCES users(username)
);