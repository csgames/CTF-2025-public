console.log( 
    String.fromCharCode(...[DATA].map(
        (c, i) => c ^ document.body.innerText.charCodeAt(i + OFFSET))
    ));
