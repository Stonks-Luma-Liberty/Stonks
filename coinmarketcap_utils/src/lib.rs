use pyo3::prelude::*;
use reqwest::blocking::Client;
use reqwest::header::{HeaderMap, HeaderValue, SET_COOKIE, USER_AGENT};
use select::document::Document;
use select::predicate::{Name, Predicate};

fn get_cookies() -> Vec<HeaderValue> {
    let response = reqwest::blocking::get("https://google.com").unwrap();
    let cookies: Vec<HeaderValue> = response
        .headers()
        .get_all("set-cookie")
        .iter()
        .map(|header_value| header_value.to_owned())
        .collect();
    cookies
}

fn construct_header() -> HeaderMap {
    let mut headers = HeaderMap::new();
    headers.insert(USER_AGENT, HeaderValue::from_str("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.79 Safari/537.36").unwrap());

    for cookie in get_cookies() {
        headers.insert(SET_COOKIE, HeaderValue::from(cookie));
    }
    headers
}

#[pyfunction]
fn get_trending_tokens() -> PyResult<Vec<String>> {
    let mut trending_tokens: Vec<String> = vec![];
    let url = "https://coinmarketcap.com/trending-cryptocurrencies";
    let client = Client::new();
    let response = client.get(url).headers(construct_header()).send().unwrap();

    let document = Document::from(response.text().unwrap().as_str());

    for node in document.find(Name("table").descendant(Name("a"))) {
        let elements: Vec<String> = node
            .find(Name("p"))
            .map(|element| element.inner_html())
            .collect();

        if !elements.is_empty() {
            trending_tokens.push(format!("{} ({})", elements[0], elements[1]));
        }
    }
    Ok(trending_tokens)
}

/// A Python module implemented in Rust.
#[pymodule]
fn coinmarketcap_utils(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(get_trending_tokens, m)?)?;
    Ok(())
}
