package main
import (
  "encoding/json"
  "fmt"
  "go/ast"
  "go/parser"
  "go/token"
  "os"
  "path/filepath"
  "sort"
  "strings"
)
type Route struct { Method string `json:"method"`; Path string `json:"path"`; File string `json:"file"`; Line int `json:"line"`; Handler string `json:"handler"` }
type Program struct { fset *token.FileSet; funcs map[string]*ast.FuncDecl; routes []Route; seen map[string]bool }
func join(a,b string) string { p:=strings.Trim(strings.TrimSpace(a),"/")+"/"+strings.Trim(strings.TrimSpace(b),"/")
 p=strings.Trim(p,"/"); if p=="" {return "/"}; return "/"+p }
func lit(e ast.Expr) string { if b,ok:=e.(*ast.BasicLit); ok { s:=strings.Trim(b.Value,"\""); return s }; return "" }
func (p *Program) exec(fn *ast.FuncDecl, initial map[string]string, file string) {
 if fn==nil || fn.Body==nil {return}
 key:=file+"::"+fn.Name.Name
 for k,v:=range initial {key+=fmt.Sprintf("|%s=%s",k,v)}
 if p.seen[key] {return}; p.seen[key]=true
 env:=map[string]string{}; for k,v:=range initial {env[k]=v}
 var walk func(ast.Node)
 walk=func(n ast.Node) {
   if n==nil{return}
   switch x:=n.(type) {
   case *ast.AssignStmt:
     for i,rhs:=range x.Rhs { if call,ok:=rhs.(*ast.CallExpr); ok { if sel,ok:=call.Fun.(*ast.SelectorExpr); ok && sel.Sel.Name=="Group" && len(call.Args)>0 {
       parent:=""; if id,ok:=sel.X.(*ast.Ident); ok {parent=env[id.Name]}; name:=""; if len(call.Args)>0{name=lit(call.Args[0])}; if i<len(x.Lhs) {if id,ok:=x.Lhs[i].(*ast.Ident);ok{env[id.Name]=join(parent,name)}}
     }} }
   case *ast.CallExpr:
     if sel,ok:=x.Fun.(*ast.SelectorExpr);ok {
       m:=sel.Sel.Name
       switch m {case "GET","POST","PUT","DELETE","PATCH","OPTIONS","HEAD":
         if len(x.Args)>0 { base:=""; if id,ok:=sel.X.(*ast.Ident);ok{base=env[id.Name]}; path:=lit(x.Args[0]); h:="";if len(x.Args)>1{h=fmt.Sprint(x.Args[1])}; pos:=p.fset.Position(x.Pos()); p.routes=append(p.routes,Route{m,join(base,path),filepath.ToSlash(file),pos.Line,h}) }
       }
     } else if id,ok:=x.Fun.(*ast.Ident);ok {
       if child:=p.funcs[id.Name]; child!=nil {
         childEnv:=map[string]string{}
         if child.Type.Params!=nil {idx:=0;for _,field:=range child.Type.Params.List {for _,nm:=range field.Names {if idx<len(x.Args){ if arg,ok:=x.Args[idx].(*ast.Ident);ok {childEnv[nm.Name]=env[arg.Name]} else {childEnv[nm.Name]=""} };idx++}}}
         p.exec(child,childEnv,file)
       }
     }
   }
   ast.Inspect(n,func(child ast.Node) bool { if child==n{return true}; walk(child); return false })
 }
 // walk statements in source order; handle compound bodies recursively
 for _,stmt:=range fn.Body.List {walk(stmt)}
}
func main(){root:=os.Args[1]; fset:=token.NewFileSet(); files:=[]string{};_ = filepath.Walk(filepath.Join(root,"router"),func(path string,info os.FileInfo,err error)error{if err==nil&&!info.IsDir()&&strings.HasSuffix(path,".go"){files=append(files,path)};return nil});sort.Strings(files)
 routes:=[]Route{}; for _,file:=range files {f,err:=parser.ParseFile(fset,file,nil,0);if err!=nil{continue};funcs:=map[string]*ast.FuncDecl{};for _,d:=range f.Decls{if fn,ok:=d.(*ast.FuncDecl);ok{funcs[fn.Name.Name]=fn}}
  p:=&Program{fset:fset,funcs:funcs,seen:map[string]bool{}}
  for _,fn:=range funcs { if fn.Name.Name=="RouterInit" {p.exec(fn,map[string]string{},file)} else if fn.Name.Name=="SSERouter" {p.exec(fn,map[string]string{"Router":"/api/v1"},file)} else if strings.HasPrefix(fn.Name.Name,"Init") && strings.HasSuffix(file,"router/apps/"+filepath.Base(file)) { // only exported app init funcs
      hasGin:=false;if fn.Type.Params!=nil{for _,field:=range fn.Type.Params.List{if sel,ok:=field.Type.(*ast.StarExpr);ok{if s,ok:=sel.X.(*ast.SelectorExpr);ok&&s.Sel.Name=="RouterGroup"{hasGin=true}}}};if hasGin{initial:=map[string]string{};if fn.Type.Params!=nil{for _,field:=range fn.Type.Params.List{for _,nm:=range field.Names{initial[nm.Name]="/api/v1";break}}};p.exec(fn,initial,file)}
    } }
  routes=append(routes,p.routes...)
 }
 b,_:=json.MarshalIndent(routes,"","  ");fmt.Println(string(b));fmt.Fprintf(os.Stderr,"registrations=%d unique=%d\n",len(routes),func()int{m:=map[string]bool{};for _,r:=range routes{m[r.Method+" "+r.Path]=true};return len(m)}())
}
