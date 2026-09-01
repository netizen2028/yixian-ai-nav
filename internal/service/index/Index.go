/**
 * @Author: chentong
 * @Date: 2024/05/26 上午1:52
 */

package index

import (
	"context"
	"encoding/json"
	"html/template"
	"sort"
	"strconv"
	"strings"

	"golang.org/x/sync/errgroup"

	v1 "github.com/ch3nnn/webstack-go/api/v1"
	"github.com/ch3nnn/webstack-go/internal/dal/model"
	"github.com/ch3nnn/webstack-go/internal/dal/query"
)

// buildTree 构建树形结构
func buildTree(nodes []*v1.TreeNode, pid int) []*v1.TreeNode {
	var treeNodes []*v1.TreeNode
	for _, node := range nodes {
		if node.Pid == pid {
			node.Child = buildTree(nodes, node.Id)
			treeNodes = append(treeNodes, node)
		}
	}
	return treeNodes
}

// categoryTree 对树形结构按 Sort 字段排序
func categoryTree(nodes []*v1.TreeNode) []*v1.TreeNode {
	sort.Slice(nodes, func(i, j int) bool {
		return nodes[i].Sort < nodes[j].Sort
	})

	for _, node := range nodes {
		if len(node.Child) > 0 {
			categoryTree(node.Child)
		}
	}
	return nodes
}

// categorySites 将站点数据归类到分类站点中
func categorySites(sites []*model.StSite, treeNodes []*v1.TreeNode) (data []*v1.CategorySite) {
	for _, node := range treeNodes {
		categorySite := &v1.CategorySite{
			Category: node.Name,
			SiteList: []model.StSite{},
		}

		for _, site := range sites {
			if site.CategoryID == node.Id {
				categorySite.SiteList = append(categorySite.SiteList, *site)
			}
		}
		//  Sort 字段进行升序排序
		sort.Slice(categorySite.SiteList, func(i, j int) bool {
			return categorySite.SiteList[i].Sort < categorySite.SiteList[j].Sort
		})

		if len(categorySite.SiteList) > 0 {
			data = append(data, categorySite)
		}

		if len(node.Child) > 0 {
			childCategorySites := categorySites(sites, node.Child)
			data = append(data, childCategorySites...)
		}
	}

	return data
}

// findCategoryName 从分类列表中查找分类名
func findCategoryName(categories []*model.StCategory, id int) string {
	for _, c := range categories {
		if c.ID == id {
			return c.Title
		}
	}
	return ""
}

// countCategorySites 统计指定分类下的站点数量
func countCategorySites(categorySites []*v1.CategorySite, name string) int {
	for _, cs := range categorySites {
		if cs.Category == name {
			return len(cs.SiteList)
		}
	}
	return 0
}

// buildCategoryDesc 生成选中分类的 description（分类表无描述字段，按分类名与收录量组装）
func buildCategoryDesc(name string, count int) string {
	if name == "" {
		return ""
	}
	return strings.TrimSpace(name) + "企业名录 - 精选收录 " + strconv.Itoa(count) + " 家企业，一站直达官网"
}

// buildJSONLD 生成 JSON-LD 结构化数据（WebSite + SearchAction，选中分类时追加 ItemList）
func buildJSONLD(cfg *model.SysConfig, categorySites []*v1.CategorySite, selectedName string) template.JS {
	siteURL := strings.TrimRight(cfg.SiteURL, "/")
	if siteURL == "" {
		siteURL = "https://2026.yixian.wiki"
	}

	graph := []map[string]interface{}{
		{
			"@type":       "WebSite",
			"@id":         siteURL + "/#website",
			"url":         siteURL + "/",
			"name":        cfg.SiteTitle,
			"description": cfg.SiteDesc,
			"publisher":   map[string]interface{}{"@id": siteURL + "/#organization"},
			"potentialAction": []map[string]interface{}{{
				"@type":       "SearchAction",
				"target":      map[string]string{"@type": "EntryPoint", "urlTemplate": siteURL + "/?s={search_term_string}"},
				"query-input": "required name=search_term_string",
			}},
		},
		{
			"@type": "Organization",
			"@id":   siteURL + "/#organization",
			"name":  cfg.SiteTitle,
			"url":   siteURL + "/",
		},
	}

	// 选中分类时，输出该分类下的站点列表
	if selectedName != "" {
		items := make([]map[string]interface{}, 0, 32)
		pos := 0
		for _, cs := range categorySites {
			if cs.Category != selectedName {
				continue
			}
			for _, site := range cs.SiteList {
				pos++
				items = append(items, map[string]interface{}{
					"@type":    "ListItem",
					"position": pos,
					"name":     site.Title,
					"url":      site.URL,
				})
			}
		}
		if len(items) > 0 {
			graph = append(graph, map[string]interface{}{
				"@type":           "ItemList",
				"name":            selectedName,
				"itemListElement": items,
			})
		}
	}

	raw, err := json.Marshal(map[string]interface{}{
		"@context": "https://schema.org",
		"@graph":   graph,
	})
	if err != nil {
		return ""
	}
	return template.JS(raw)
}

// Index 获取首页数据
func (s *service) Index(ctx context.Context, categoryID int) (*v1.IndexResp, error) {
	var (
		g          errgroup.Group
		sysConfig  *model.SysConfig
		sites      []*model.StSite
		categories []*model.StCategory
	)

	g.Go(func() (err error) {
		categories, err = s.categoryRepo.WithContext(ctx).FindAllOrderBySort(query.StCategory.Sort.Abs(), s.categoryRepo.WhereByIsUsed(true))
		return err
	})

	g.Go(func() (err error) {
		sites, err = s.siteRepo.WithContext(ctx).FindAll(s.siteRepo.WhereByIsUsed(true))
		return err
	})

	g.Go(func() (err error) {
		sysConfig, err = s.configRepo.WithContext(ctx).FindOne()
		return err
	})

	if err := g.Wait(); err != nil {
		return nil, err
	}

	nodes := make([]*v1.TreeNode, len(categories))
	for i, category := range categories {
		nodes[i] = &v1.TreeNode{
			Id:   category.ID,
			Pid:  category.ParentID,
			Name: category.Title,
			Icon: category.Icon,
			Sort: category.Sort,
		}
	}

	categoryTree := categoryTree(buildTree(nodes, 0))
	categorySites := categorySites(sites, categoryTree)

	// 选中的分类（?category=N）：仅用于标题 / canonical / JSON-LD，页面仍展示全部分类并锚点定位
	var selectedName string
	if categoryID > 0 {
		selectedName = findCategoryName(categories, categoryID)
		if selectedName == "" {
			// 分类不存在或已下线时不作为选中项，避免出现无效 canonical
			categoryID = 0
		}
	}

	return &v1.IndexResp{
		ConfigSite: &v1.ConfigSite{
			SiteTitle:   sysConfig.SiteTitle,
			SiteKeyword: sysConfig.SiteKeyword,
			SiteDesc:    sysConfig.SiteDesc,
			SiteRecord:  sysConfig.SiteRecord,
			SiteURL:     sysConfig.SiteURL,
			SiteLogo:    sysConfig.SiteLogo,
			SiteFavicon: sysConfig.SiteFavicon,
		},
		About: &v1.About{
			AboutSite:   sysConfig.AboutSite,
			AboutAuthor: sysConfig.AboutAuthor,
			IsAbout:     sysConfig.IsAbout,
		},
		CategoryTree:         categoryTree,
		CategorySites:        categorySites,
		SelectedCategoryID:   categoryID,
		SelectedCategoryName: selectedName,
		SelectedCategoryDesc: buildCategoryDesc(selectedName, countCategorySites(categorySites, selectedName)),
		JSONLD:               buildJSONLD(sysConfig, categorySites, selectedName),
	}, nil
}
