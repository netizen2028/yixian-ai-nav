/**
 * @Author: chentong
 * @Date: 2024/05/26 上午1:50
 */

package v1

import (
	"html/template"

	"github.com/ch3nnn/webstack-go/internal/dal/model"
)

type TreeNode struct {
	Id    int         // 节点ID
	Pid   int         // 父节点ID
	Name  string      // 节点名称
	Icon  string      // 图标
	Sort  int         // 排序
	Child []*TreeNode // 获取子节点切片
}

type CategorySite struct {
	Category string         // 分类
	SiteList []model.StSite // 站点列表
}

type About struct {
	AboutSite   string `json:"about_site"`   // 关于站点
	AboutAuthor string `json:"about_author"` // 关于作者
	IsAbout     bool   `json:"is_about"`     // 是否开启关于
}

type ConfigSite struct {
	SiteTitle   string `json:"site_title"`   // 站点标题
	SiteKeyword string `json:"site_keyword"` // 站点关键字
	SiteDesc    string `json:"site_desc"`    // 站点描述
	SiteRecord  string `json:"site_record"`  // 站点备案
	SiteURL     string `json:"site_url"`     // 备案url
	SiteLogo    string `json:"site_logo"`    // 站点logo
	SiteFavicon string `json:"site_favicon"` // 站点favicon
}

type IndexResp struct {
	About                *About          // 关于页面
	ConfigSite           *ConfigSite     // 站点配置
	CategoryTree         []*TreeNode     // 分类树
	CategorySites        []*CategorySite // 归类站点数据
	SelectedCategoryID   int             // 当前选中分类ID（来自 ?category=N，0 表示未选中）
	SelectedCategoryName string          // 当前选中分类名（未选中时为空）
	SelectedCategoryDesc string          // 当前选中分类的 description（未选中时为空，回退站点描述）
	JSONLD               template.JS     // JSON-LD 结构化数据（已序列化，模板内原样输出）
}

type AboutResp struct {
	About
}
